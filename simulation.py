
import matplotlib.pyplot as plt
import supply_chain
import json


def plot_data(simulation):
    figure = plt.figure()
    retailer_plot = figure.add_subplot(221)
    wholesaler_plot = figure.add_subplot(222)
    distributor_plot = figure.add_subplot(223)
    factory_plot = figure.add_subplot(224)

    # retailer
    _generate_plot(retailer_plot, simulation.retailer.weekly_inventory, simulation.retailer.weekly_backlog,
                   simulation.retailer.weekly_order, "Retailer")

    # wholesaler
    _generate_plot(wholesaler_plot, simulation.wholesaler.weekly_inventory, simulation.wholesaler.weekly_backlog,
                   simulation.wholesaler.weekly_order, "Wholesaler")

    # distributor
    _generate_plot(distributor_plot, simulation.distributor.weekly_inventory, simulation.distributor.weekly_backlog,
                   simulation.distributor.weekly_order, "Distributor")

    # factory
    _generate_plot(factory_plot, simulation.factory.weekly_inventory, simulation.factory.weekly_backlog,
                   simulation.factory.weekly_order, "Factory")
    plt.show()


def _generate_plot(supply_plot, weekly_inventory, weekly_backlog, weekly_order, supply_chain_tier):
    supply_plot.plot(weekly_inventory)
    supply_plot.plot(weekly_backlog)
    supply_plot.plot(weekly_order)
    supply_plot.set_title(f'{supply_chain_tier} simulation over Time')
    supply_plot.set_ylabel('Units of Inventory')
    supply_plot.set_xlabel('Week')
    supply_plot.legend(['Inventory', "Backlog", "Orders"], loc='upper left')


def load_config(path="game_config.json"):
    with open(path, "r") as fd:
        config = json.load(fd)
        assert config["total_turns"] == len(config["weekly_customer_demand"])
        return config


def retailer_decision_making(retailer):
    # Implement decision making logic for retailer
    return 6


def wholesaler_decision_making(wholesaler):
    # Implement decision making logic for wholesaler
    return 6


def distributor_decision_making(distributor):
    # Implement decision making logic for distributor
    return 6


def factory_decision_making(factory):
    # Implement decision making logic for factory
    return 6


def main():
    config = load_config("optimal_config.json")
    simulation = supply_chain.SupplyChainSimulation(**{**config["initial_setup"]["retailer"],
                                                       **config["initial_setup"]["wholesaler"],
                                                       **config["initial_setup"]["distributor"],
                                                       **config["initial_setup"]["factory"]})
    if config["weekly_retailer_decision"] and config["weekly_wholesaler_decision"] and \
            config["weekly_distributor_decision"] and config["weekly_factory_decision"]:
        print("Using Config...\n")
        for i in range(config["total_turns"]):
            simulation.turn(config["weekly_customer_demand"][i], config["weekly_retailer_decision"][i],
                            config["weekly_wholesaler_decision"][i], config["weekly_distributor_decision"][i],
                            config["weekly_factory_decision"][i])
        print(simulation)
        plot_data(simulation)
    else:
        for i in range(config["total_turns"]):
            print("Using dynamic logic...\n")
            retailer_decision = retailer_decision_making(simulation.retailer)
            wholesaler_decision = wholesaler_decision_making(simulation.wholesaler)
            distributor_decision = distributor_decision_making(simulation.distributor)
            factory_decision = factory_decision_making(simulation.factory)

            simulation.turn(config["weekly_customer_demand"][i], retailer_decision, wholesaler_decision,
                            distributor_decision, factory_decision)
        print(simulation)


if __name__ == "__main__":
    main()
