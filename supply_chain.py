import sys

HOLDING_COST = 0.5
BACKORDER_COST = 1.0


class SupplyChain:
    def __init__(self, inventory=0, shipping_delays=(0, 0), order_delays=(0, 0)):

        self.current_inventory = inventory

        # Shipping delay acts as production delay for Factory
        self.shipping_delay_1 = shipping_delays[1]
        self.shipping_delay_2 = shipping_delays[0]

        self.order_delay_1 = order_delays[1]
        self.order_delay_2 = order_delays[0]

        self.weekly_backlog = []
        self.weekly_inventory = []
        self.weekly_order = []

    def __str__(self):
        return f'Weekly Inventory: {self.weekly_inventory}({sum(self.weekly_inventory)*HOLDING_COST})\n' \
               f'Weekly Backlog: {self.weekly_backlog} ({sum(self.weekly_backlog)*BACKORDER_COST})\n' \
               f'Weekly Order: {self.weekly_order}'

    def receive_inventory(self):
        self.current_inventory += self.shipping_delay_2
        self.shipping_delay_2 = self.shipping_delay_1
        self.shipping_delay_1 = 0

    def fill_orders(self, other=None, *args, **kwargs):
        assert other
        backlog = self.weekly_backlog[-1] if self.weekly_backlog else 0
        needed_quantity = backlog + self.order_delay_2
        new_backlog = 0
        if self.current_inventory >= needed_quantity:
            other.shipping_delay_1 += needed_quantity
            self.current_inventory -= needed_quantity
        else:
            new_backlog = needed_quantity - self.current_inventory
            other.shipping_delay_1 += self.current_inventory
            self.current_inventory = 0

        self.weekly_inventory.append(self.current_inventory)
        self.weekly_backlog.append(new_backlog)

    def advance_orders(self, *args, **kwargs):
        self.order_delay_2 = self.order_delay_1
        self.order_delay_1 = 0

    def place_order(self, decision_order, other=None, *args, **kwargs):
        other.order_delay_1 = decision_order
        self.weekly_order.append(decision_order)

    def get_costs(self):
        return sum(self.weekly_inventory)*HOLDING_COST + sum(self.weekly_backlog)*BACKORDER_COST


class Retailer(SupplyChain):
    def __init__(self, inventory=0, shipping_delays=(0, 0)):
        super().__init__(inventory=inventory, shipping_delays=shipping_delays)

    def fill_orders(self, other=None, customer_demand=4, *args, **kwargs):
        backlog = self.weekly_backlog[-1] if self.weekly_backlog else 0
        needed_quantity = backlog + customer_demand
        new_backlog = 0
        if self.current_inventory >= needed_quantity:
            self.current_inventory -= needed_quantity
        else:
            new_backlog = needed_quantity - self.current_inventory
            self.current_inventory = 0

        self.weekly_inventory.append(self.current_inventory)
        self.weekly_backlog.append(new_backlog)

    def advance_orders(self, *args, **kwargs):
        pass


class Factory(SupplyChain):
    def __init__(self, inventory=0, shipping_delays=(0, 0), order_delays=(0, 0), initial_factory_request=4):
        super().__init__(inventory=inventory, shipping_delays=shipping_delays, order_delays=order_delays)
        self.factory_request = initial_factory_request

    def advance_orders(self, *args, **kwargs):
        super().advance_orders()
        self.shipping_delay_1 += self.factory_request

    def place_order(self, decision_order, *args, **kwargs):
        self.factory_request = decision_order
        self.weekly_order.append(decision_order)


class SupplyChainSimulation:
    def __init__(self, retailer_inventory=4, retailer_shipping_delays=(4, 4),
                 wholesaler_inventory=4, wholesaler_shipping_delays=(4, 4), wholesaler_order_delays=(4, 4),
                 distributor_inventory=4, distributor_shipping_delays=(4, 4), distributor_order_delays=(4, 4),
                 factory_inventory=4, factory_shipping_delays=(4, 4), factory_order_delays=(4, 4),
                 factory_initial_factory_request=4):
        self.retailer = Retailer(inventory=retailer_inventory, shipping_delays=retailer_shipping_delays)
        self.wholesaler = SupplyChain(inventory=wholesaler_inventory, shipping_delays=wholesaler_shipping_delays,
                                      order_delays=wholesaler_order_delays)
        self.distributor = SupplyChain(inventory=distributor_inventory, shipping_delays=distributor_shipping_delays,
                                       order_delays=distributor_order_delays)
        self.factory = Factory(inventory=factory_inventory, shipping_delays=factory_shipping_delays,
                               order_delays=factory_order_delays,
                               initial_factory_request=factory_initial_factory_request)

    def _receive_all_incoming_inventory(self):
        self.retailer.receive_inventory()
        self.wholesaler.receive_inventory()
        self.distributor.receive_inventory()
        self.factory.receive_inventory()

    def _fill_all_customer_orders(self, customer_demand):
        self.retailer.fill_orders(other=None, customer_demand=customer_demand)
        self.wholesaler.fill_orders(other=self.retailer)
        self.distributor.fill_orders(other=self.wholesaler)
        self.factory.fill_orders(other=self.distributor)

    def _advance_all_orders(self):
        self.retailer.advance_orders()
        self.wholesaler.advance_orders()
        self.distributor.advance_orders()
        self.factory.advance_orders()

    def _place_all_orders(self, retailer_decision, wholesaler_decision, distributor_decision, factory_decision):
        self.retailer.place_order(retailer_decision, other=self.wholesaler)
        self.wholesaler.place_order(wholesaler_decision, other=self.distributor)
        self.distributor.place_order(distributor_decision, other=self.factory)
        self.factory.place_order(factory_decision)

    def turn(self, customer_demand, retailer_decision, wholesaler_decision, distributor_decision, factory_decision):
        self._receive_all_incoming_inventory()
        self._fill_all_customer_orders(customer_demand)
        self._advance_all_orders()
        self._place_all_orders(retailer_decision, wholesaler_decision, distributor_decision, factory_decision)

    def __str__(self):
        total_cost = self.retailer.get_costs() + self.wholesaler.get_costs() + self.distributor.get_costs() + \
                     self.factory.get_costs()
        return f'-- Retailer --\n{str(self.retailer)}\n\n' \
               f'-- Wholesaler --\n{str(self.wholesaler)}\n\n' \
               f'-- Distributor --\n{str(self.distributor)}\n\n' \
               f'-- Factory --\n{str(self.factory)}\n\n' \
               f'Total Costs: ({total_cost})'


def main(turns):
    simulation = SupplyChainSimulation()
    for i in range(int(turns)):
        print(f"------------ TURN {i} ------------")
        customer_demand = int(input("Enter Customer Demand: "))
        retailer_decision = int(input("Enter Retailer Order Decision: "))
        wholesaler_decision = int(input("Enter Wholesaler Order Decision: "))
        distributor_decision = int(input("Enter Distributor Order Decision: "))
        factory_decision = int(input("Enter Factory Order Decision: "))
        simulation.turn(customer_demand, retailer_decision, wholesaler_decision, distributor_decision, factory_decision)
    print(simulation)


if __name__ == '__main__':
    main(sys.argv[1])
