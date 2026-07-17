import os
from pos_app.models.sale import Sale
from pos_app.config.settings import settings

class ReceiptService:
    def __init__(self, session_db):
        self.session_db = session_db

    def generate_receipt_text(self, sale_id: int) -> str:
        """Generate a formatted receipt layout for receipt printers."""
        sale = self.session_db.query(Sale).filter(Sale.id == sale_id).first()
        if not sale:
            return "Transaction not found."
            
        from pos_app.models.sale_item import SaleItem
        from pos_app.models.product import Product
        from pos_app.models.payment import Payment
        from pos_app.models.user import User
        
        items = self.session_db.query(SaleItem).filter(SaleItem.sale_id == sale_id).all()
        payments = self.session_db.query(Payment).filter(Payment.sale_id == sale_id).all()
        cashier = self.session_db.query(User).filter(User.id == sale.cashier_id).first()
        cashier_name = cashier.full_name if cashier else "Staff"
        
        lines = []
        lines.append(settings.STORE_NAME.center(40))
        lines.append(settings.STORE_ADDRESS.center(40))
        lines.append(settings.STORE_PHONE.center(40))
        lines.append(f"Tax ID: {settings.STORE_TAX_ID}".center(40))
        lines.append("-" * 40)
        lines.append(f"Invoice: {sale.invoice_no}")
        lines.append(f"Date: {sale.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Cashier: {cashier_name}")
        lines.append("-" * 40)
        lines.append(f"{'Item':<20} {'Qty':>4} {'Price':>6} {'Total':>7}")
        lines.append("-" * 40)
        
        for item in items:
            p = self.session_db.query(Product).filter(Product.id == item.product_id).first()
            p_name = p.name[:18] if p else f"Item #{item.product_id}"
            qty_str = f"{item.qty:.1f}" if item.qty % 1 != 0 else f"{int(item.qty)}"
            lines.append(f"{p_name:<20} {qty_str:>4} {settings.CURRENCY}{item.unit_price:>5.2f} {settings.CURRENCY}{item.line_total:>6.2f}")
            if item.discount > 0:
                lines.append(f"  * Discount: -{settings.CURRENCY}{item.discount:.2f}")
                
        lines.append("-" * 40)
        lines.append(f"{'Subtotal:':<25} {settings.CURRENCY}{sale.subtotal:>13.2f}")
        if sale.discount_total > 0:
            lines.append(f"{'Discount Total:':<25} -{settings.CURRENCY}{sale.discount_total:>12.2f}")
        lines.append(f"{'Tax:':<25} {settings.CURRENCY}{sale.tax_total:>13.2f}")
        lines.append(f"{'Grand Total:':<25} {settings.CURRENCY}{sale.grand_total:>13.2f}")
        lines.append("-" * 40)
        
        for pm in payments:
            lines.append(f"{pm.method + ' Tendered:':<25} {settings.CURRENCY}{pm.amount:>13.2f}")
            
        lines.append("-" * 40)
        lines.append("Thank you for your business!".center(40))
        lines.append("Please retain this receipt for return".center(40))
        lines.append("\n\n")
        
        return "\n".join(lines)

    def print_to_physical_printer(self, sale_id: int) -> bool:
        """Send raw receipt text and ESC/POS escape sequences to a physical thermal receipt printer."""
        receipt_text = self.generate_receipt_text(sale_id)
        
        # ESC/POS standard control sequences
        ESC_INIT = b'\x1b\x40'
        ESC_CENTER = b'\x1b\x61\x01'
        ESC_LEFT = b'\x1b\x61\x00'
        ESC_FEED_CUT = b'\x1b\x64\x05\x1d\x56\x41\x00' # feed 5 lines and partial cut
        
        print(f"[*] Compiling ESC/POS binary print job for Sale #{sale_id}...")
        
        payload = bytearray()
        payload.extend(ESC_INIT)
        
        for line in receipt_text.split('\n'):
            stripped = line.strip()
            # If the line is store header or thanks message, center-align it
            if stripped == settings.STORE_NAME or stripped == "Thank you for your business!" or stripped == "Please retain this receipt for return":
                payload.extend(ESC_CENTER)
            else:
                payload.extend(ESC_LEFT)
            payload.extend(line.encode('utf-8') + b'\n')
            
        payload.extend(ESC_FEED_CUT)
        
        # 1. Attempt PyUSB connection to USB receipt printers (Interface Class 7)
        usb_printed = False
        try:
            import usb.core
            import usb.util
            
            # Search all connected USB devices
            devices = list(usb.core.find(find_all=True))
            print(f"[*] Scanning {len(devices)} USB device(s) for printer interface...")
            for dev in devices:
                for cfg in dev:
                    for intf in cfg:
                        if intf.bInterfaceClass == 7: # Printer Class
                            print(f"[+] Found USB Printer: Vendor ID {hex(dev.idVendor)}, Product ID {hex(dev.idProduct)}")
                            if dev.is_kernel_driver_active(intf.bInterfaceNumber):
                                try:
                                    dev.detach_kernel_driver(intf.bInterfaceNumber)
                                except Exception as de:
                                    print(f"[*] Detach kernel driver warning: {de}")
                                    
                            dev.set_configuration()
                            # Find the OUT endpoint
                            ep = usb.util.find_descriptor(
                                intf,
                                custom_match=lambda e: \
                                    usb.util.endpoint_direction(e.bEndpointAddress) == \
                                    usb.util.ENDPOINT_OUT
                            )
                            if ep:
                                ep.write(payload)
                                usb_printed = True
                                print("[+] Successfully dispatched job via PyUSB endpoint write.")
                                break
                    if usb_printed:
                        break
                if usb_printed:
                    break
        except Exception as e:
            print(f"[!] PyUSB pipeline exception: {e}")

        # 2. Fallback to direct raw serial device writes
        serial_printed = False
        if not usb_printed:
            print("[*] PyUSB print failed or no device found. Probing direct serial ports...")
            try:
                import serial
                ports = ['/dev/usb/lp0', '/dev/lp0', '/dev/ttyUSB0', '/dev/ttyAMA0', 'COM1', 'COM2', 'COM3', 'COM4']
                for p in ports:
                    if os.path.exists(p) or (os.name == 'nt' and p.startswith('COM')):
                        try:
                            ser = serial.Serial(p, 9600, timeout=1)
                            ser.write(payload)
                            ser.close()
                            serial_printed = True
                            print(f"[+] Successfully dispatched job to serial port: {p}")
                            break
                        except Exception as se:
                            print(f"[*] Serial port write error on {p}: {se}")
            except Exception as e:
                print(f"[!] PySerial pipeline exception: {e}")
                
        return usb_printed or serial_printed

