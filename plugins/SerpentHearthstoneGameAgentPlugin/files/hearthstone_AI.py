# Handles actions that require thinking
class HearthstoneAI:

    # Decides what to mulligan based solely on mana threshold
    @staticmethod
    def get_mulligan(hand):
        mull = []
        for card in hand:
            if card.cost >= 3:
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
                to_play.append(hand.hand[i].name)
                # to_play.append(hand.hand[i].position)
                cost = mana - hand.hand[i].cost
                value += hand.hand[i].value
                if cost >= 0:
                    temp_chain, temp_max_value = dfs(hand, cost, i+1, max_value, value, to_play)
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

        chain, val = dfs(hand, mana, 0, 0, 0, [])
        return chain, val

    @staticmethod
    # Kill taunts if they exist, then go face
    # board variable of type Board
    def simple_smorc(board):
        pass
            
    @staticmethod
    # Kills taunts efficiently by taking value trades and minimizing overkill    
    # board variable of type Board
    def smarter_smorc(board):
        pass
