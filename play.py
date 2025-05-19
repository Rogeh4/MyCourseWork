from pong_game import PongGame
from q_learning_agent import QLearningAgent


def main():
    game = PongGame()
    agent = QLearningAgent()
    agent.load_model("best_model.pkl")

    while True:
        state = game.discretize_state(game.get_state())
        action = agent.choose_action(state)
        game.step(action)


if __name__ == "__main__":
    main()