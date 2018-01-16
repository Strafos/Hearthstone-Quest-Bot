import time

# Handles actions that require thinking
class HearthstoneAI:

    # Decides what to mulligan based solely on mana threshold
    @staticmethod
    def get_mulligan(hand):
        mull = []
        for card in hand:
            if len(hand) == 4 and card.cost >= 3:
                mull.append(card.position)
            if len(hand) == 6 and card.cost >= 4:
                mull.append(card.position)
        return mull

    # Return an array of cards to play this turn
    # Makes most efficient use of mana using DFS 
    @staticmethod
    def play_card(hand, mana):
        # TODO how does Corridor Creeper work?
        # Precondition: Hand sorted by increasing cost
        def dfs(hand, mana, idx, max_value, value, to_play):
            chain = []
            if mana >= 0 and value > max_value:
                chain = to_play[:]
                max_value = value
            for i in range(idx, hand.size):
                if hand.hand[i].name == "The Coin":
                    remaining_mana = mana + 1
                else:
                    remaining_mana = mana - hand.hand[i].cost
                to_play.append((hand.hand[i].position, hand.hand[i].cost, hand.hand[i].value))
                value += hand.hand[i].value
                if remaining_mana >= 0:
                    temp_chain, temp_max_value = dfs(hand, remaining_mana, i+1, max_value, value, to_play)
                    if temp_max_value > max_value:
                        chain = temp_chain
                        max_value = temp_max_value
                else:
                    value -= hand.hand[i].value
                    to_play.pop()
                    break
                value -= hand.hand[i].value
                to_play.pop()
            return chain, max_value

        temp_chain, val = dfs(hand, mana, 0, 0, 0, [])
        if len(temp_chain) > 1:
            tot_cost = 0
            for elem in temp_chain[1:]:
                tot_cost += elem[1]
            if tot_cost == mana:
                # Don't use coin if not needed for play
                del temp_chain[0]
        
        # Sort by increasing value
        temp_chain.sort(key=lambda elem: elem[2], reverse=True)
        
        chain = []
        coin = False
        for elem in temp_chain:
            if elem[1] == 0 and elem[2] == 0:
                coin_elem = elem
                coin = True
            chain.append(elem[0])
        if coin:
            chain.insert(0, coin_elem[0])

        return chain, val

    @staticmethod
    # Kill taunts if they exist, then go face
    # board variable of type Board
    # Does not use weapons
    def simple_smorc(board):
        # Identify current taunters and attackers
        taunters = []
        for enemy in board.enemy_minions:
            if enemy.taunt:
                taunters.append(enemy)
        attackers = []
        for ally in board.ally_minions:
            if ally.attack > 0 and not ally.exhausted:
                attackers.append(ally)
        
        chain = []
        k = 0
        for enemy in taunters:
            health = enemy.health
            while health > 0 and k < len(attackers):
                chain.append((attackers[k].position, enemy.position))
                health -= attackers[k].attack
                k += 1
        
        for i in range(k, len(attackers)):
            chain.append((attackers[i].position, 0))
        
        return chain
            
    @staticmethod
    # Kills taunts efficiently by taking value trades and minimizing overkill    
    # board variable of type Board
    def smarter_smorc(board):
        # Identify enemy taunt minions
        taunters = []
        tot_def = 0
        for enemy in board.enemy_minions:
            if enemy.taunt:
                taunters.append(enemy)
                tot_def += enemy.health

        # Identify ally attacking minions
        attackers = []
        tot_atk = 0
        for ally in board.ally_minions:
            if ally.attack > 0 and not ally.exhausted:
                attackers.append(ally)
                tot_atk += ally.attack

        if tot_def > tot_atk:
            return []

        if len(taunters) == 0:
            chain = []
            for i in range(len(attackers)):
                chain.append((attackers[i].position, 0))
            return chain

        ## Find attack pattern that most efficiently kills
        def dfs(attackers, health, enemy_pos, idx, chain, best, best_chain):
            if health <= 0 and health > best:
                return chain, health

            for i in range(idx, len(attackers)):
                health -= attackers[i].attack
                chain.append((attackers[i].position, enemy_pos))

                new_attackers = attackers[:]
                del new_attackers[i]

                if health > best:
                    temp_chain, temp_best = dfs(new_attackers, health, enemy_pos, i+1, chain, best, best_chain)
                    if temp_best > best:
                        best_chain = temp_chain[:]
                        best = temp_best
                else:
                    health += attackers[i].attack
                    chain.pop()
                    break

                health += attackers[i].attack
                chain.pop()
            return best_chain, best

        # Optimize attack pattern for first taunt minion
        enemy = taunters[0]
        health = enemy.health
        if board.weapon:
            attackers.append(board.weapon)
        attackers.sort(key= lambda card: card.attack)
        chain, best = dfs(attackers, health, enemy.position, 0, [], -1000, [])
        return chain