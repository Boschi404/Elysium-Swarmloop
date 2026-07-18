"""
Legacy order processing module.
Contains intentional anti-patterns for code review exercise.
"""

class OrderManager:
    """GOD OBJECT: Does everything — orders, inventory, payments, shipping, reporting."""
    
    def __init__(self):
        self.orders = []
        self.total_revenue = 0
        self.inventory = {"gadget": 50, "widget": 100, "gizmo": 25, "doodad": 200}
        self.shipped = {}
        self.log = []
    
    # --- MAGIC NUMBERS scattered everywhere ---
    
    def calculate_total(self, base_price, item_type, quantity):
        """MAGIC NUMBERS: 1.15, 1.10, 1.05, 100, 0.02 are unexplained."""
        if item_type == "gadget":
            tax = base_price * 0.15  # 0.15 = ???
            discount = 0.05 if quantity >= 50 else 0
        elif item_type == "widget":
            tax = base_price * 0.10
            discount = 0.02 if quantity >= 100 else 0
        else:
            tax = base_price * 0.05
            discount = 0
        return base_price + tax - (base_price * discount)
    
    def process_order(self, customer, items, urgent, apply_warranty, 
                      gift_wrap, expedite, notify_customer):
        """BOOLEAN TRAP PARAMETER: 6 positional params, 4 are booleans. 
        Caller writes: process_order("Alice", [...], True, False, True, False, True)
        Can't tell what True/False means without reading signature."""
        
        # COPY-PASTE DUPLICATION: nearly identical blocks for each item
        for item in items:
            if item[0] == "gadget":
                price = item[1]
                if self.inventory["gadget"] >= item[2]:
                    self.inventory["gadget"] -= item[2]
                    self.orders.append(("gadget", item[2], price * item[2]))
                    self.total_revenue += price * item[2]
                else:
                    self.log.append("gadget out of stock")
                    
            elif item[0] == "widget":
                price = item[1]
                if self.inventory["widget"] >= item[2]:
                    self.inventory["widget"] -= item[2]
                    self.orders.append(("widget", item[2], price * item[2]))
                    self.total_revenue += price * item[2]
                else:
                    self.log.append("widget out of stock")
                    
            elif item[0] == "gizmo":
                price = item[1]
                if self.inventory["gizmo"] >= item[2]:
                    self.inventory["gizmo"] -= item[2]
                    self.orders.append(("gizmo", item[2], price * item[2]))
                    self.total_revenue += price * item[2]
                else:
                    self.log.append("gizmo out of stock")
        
        # SHOTGUN SURGERY: shipping cost formula duplicated here
        total_w = sum(i[1] for i in items if i[0] == "widget")
        if total_w > 100:
            shipping = 0  # free if over 100
        else:
            shipping = total_w * 0.02
        
        if urgent:
            shipping += total_w * 0.05  # 5% surcharge
        self.total_revenue += shipping
        return {"customer": customer, "items": items, "total": self.total_revenue}
    
    def get_report(self):
        """MAGIC NUMBER: 250 is unexplained."""
        report = "--- SALES REPORT ---\n"
        if len(self.orders) > 250:
            report += "HIGH VOLUME: Consider bulk discounts.\n"
        report += f"Revenue: ${self.total_revenue:.2f}\n"
        report += f"Orders: {len(self.orders)}\n"
        return report
    
    def refund(self, order_index, reason, partial, override_policy):
        """SHOTGUN SURGERY: refund logic uses same hardcoded rules."""
        if order_index < len(self.orders):
            order = self.orders[order_index]
            refund_amount = order[2] * 0.85  # 85% refund policy
            if partial:
                refund_amount *= 0.5
            self.total_revenue -= refund_amount
            self.log.append(f"Refund: {order[0]} reason={reason}")
            return refund_amount
        return 0
    
    def export_summary(self):
        """COPY-PASTE: Similar to get_report but with slightly different format."""
        summary = ""
        for o in self.orders:
            summary += f"{o[0]}: qty={o[1]} total=${o[2]:.2f}\n"
        if self.total_revenue > 10000:
            summary += "BONUS: Revenue threshold exceeded!\n"
        return summary
