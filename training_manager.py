import network, peggle_manager, fitness_manager

def minimizeFunction(guess: list[float], number_of_games: int, layer_sizes: list[int], network_controller_template, options = {}):
    weights = network.listToWeights(guess, layer_sizes)
    #print("minimize called")
    return -testNetworkFromWeights(weights, number_of_games, layer_sizes, network_controller_template, options)

def testNetworkFromWeights(weights: list[list[list[float]]], number_of_games: int, layer_sizes: list[int], network_controller_template, options = {}):
    manager = peggle_manager.Manager()
    network_to_test = network.Network(len(weights), layer_sizes)
    network_to_test.setWeights(weights)

    test_out = testNetworks(manager, number_of_games, [(0, network_to_test)], network_controller_template, options)
    print(test_out)
    return test_out[0][0]

def debugNetworkWeightSum(network: network.Network):
    sum = 0
    for a in network.weights:
        for b in a:
            for c in b:
                sum += abs(c)
    return sum

# run a number of games to test the effectiveness of the network we've trained
# return a score: the number of games won
def testNetworks(manager: peggle_manager.Manager,
             number_of_games_each: int,
             generation: list[tuple[int, network.Network]],
             network_controller_template,
             options = {}) -> tuple[int, network.Network]:
    manager.wipeHistory()
    manager.wipeResults()

    games = []
    # make a new player from the template
    for i in range(0, len(generation)):
        network = generation[i][1]
        player = network_controller_template("controller_n%d" %(i), network)
        games.append((player, number_of_games_each))

    manager.runGames(games, options)
    for game_id in manager.results.keys():
        # extract the index of the network we're dealing with
        controller_index = int(game_id.split("_")[1][1:])
        network_score = manager.results[game_id]["score"] * (1 if manager.results[game_id]["orange_pegs_left"] > 0 else 2)
        generation[controller_index] = (generation[controller_index][0] + network_score, generation[controller_index][1])

    return generation

def trainNetwork(generations: int,
                    generation_size: int,
                    base_tests_per_child: int,
                    layer_sizes: list[int],
                    network_controller_template,
                    options = {},
                    verbose = False,
                    debug = False) -> tuple[float, network.Network, dict, dict]:
    manager = peggle_manager.Manager()
    # set our seed
    seed = (0, network.Network(len(layer_sizes), layer_sizes))

    for i in range(1, generations + 1):
        generation = []
        # first, generate a lot of randomly jostled networks
        # if this is the first generation, make 10x more than usual
        for j in range(0, (10 * generation_size if i == 1 else generation_size)):
            # make a new network based on the seed
            child_network = network.Network(len(layer_sizes), layer_sizes)
            child_network.setWeights(seed[1].weights)
            # jostle amount as a function of how many generations (i) and which child (j)
            # effectively, i increase precision over time
            # and every generation, j produce more networks close to the seed, and less far away  
            magnitude = (j/10 if i == 1 else j)/i
            child_network.jostleSelf(magnitude**0.5)
            generation.append((0, child_network))

        total_tests = 0
        step = 0
        while len(generation) > 1:
            step += 1
            # list for networks and their scores during this step
            step_generation = []
            target_survivor_count = len(generation)/(2*step)

            # test each network. give them a score.
            # the # of tests increases as we refine our selection
            tests = round(base_tests_per_child * 2**(step - 1))
            total_tests += tests

            step_generation = testNetworks(manager, tests, generation, network_controller_template, options)
            generation = []

            # debug code that activates if verbose is on
            # tells about the scores of contestants in the training process for each round
            if debug and verbose:
                debug_scores = []
                for child in step_generation:
                    debug_scores.append(child[0])

                debug_sum = 0
                for score in debug_scores: debug_sum += score

                debug_scores.sort(reverse=True)
                print(debug_scores)
                print("gen %d step %d average: %.2f" %(i, step, debug_sum/len(step_generation)/total_tests))

            # pop off the best math.ceil(len(generation)/(2*step)) players
            while len(generation) < target_survivor_count:
                best = fitness_manager.getHighestScoringPlayer(step_generation)
                generation.append(best)

        # get our new seed and loop back
        seed = generation[0]

        # optional debug info about the seed we just trained
        # keeps track of the networks between generations
        if debug:
            print("generation %d final proficiency: %.2f" %(i, seed[0]/total_tests))
            print("---------------")

    # get a final result to test the effectiveness of the model
    score = testNetworks(manager, 50, [(0, seed[1])], network_controller_template, options)[0][0]

    # explicitly print results if we are verbose
    if verbose:
        print("TRAINING PARAMETERS:")
        print("Generations: %d" %(generations))
        print("Children tested per generation: %d" %(generation_size))
        print("Base # of test-games per child: %d" %(base_tests_per_child))
        print("---------------")
        print("Balls used: %s" %(10 if "balls" not in options.keys() else options["balls"]))
        print("---------------")
        print("RESULTS:")
        print("Network proficiency: %.2f" %(score/50))

    return (score, seed[1], manager)