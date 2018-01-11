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
            if mana >= 0 and value > max_value:
                chain = to_play
                max_value = value
            for i in range(idx, len(hand)):
                to_play.append(i)
                cost = mana - hand[i].cost
                if cost >= 0:
                    print(hand)
                    print(hand[i].name)
                    print(hand[i].value)
                    print(value + hand[i].value)
                    chain, val = dfs(hand, cost, i+1, max_value, value + hand[i].value, to_play)
                else:
                    break
                to_play.pop()
            return chain, max_value

        chain, val = dfs(hand, mana, 0, 0, 0, [])
        print(chain)
        return chain

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
