import pygame
from pong_game import PongGame
from q_learning_agent import QLearningAgent
import os


def main():
    game = PongGame()
    agent = QLearningAgent()

    if os.path.exists("best_model.pkl"):
        agent.load_model("best_model.pkl")

    try:
        while True:
            state = game.discretize_state(game.get_state())
            action = agent.choose_action(state)

            next_state_raw, reward, done = game.step(action)
            next_state = game.discretize_state(next_state_raw)

            agent.update_q_table(state, action, reward, next_state)

            agent.decay_epsilon()

            if done:
                game.reset()
                agent.episode += 1
                print(f"Episode: {agent.episode}, Epsilon: {agent.epsilon:.2f}, Score: {game.l_score}-{game.r_score}")

                # Сохранение модели каждые 100 эпизодов
                if agent.episode % 100 == 0:
                    agent.save_model(f"models/model_ep{agent.episode}.pkl")
                    agent.save_model("best_model.pkl")

    except KeyboardInterrupt:
        print("Training interrupted. Saving final model...")
        agent.save_model("final_model.pkl")
        pygame.quit()


if __name__ == "__main__":
    os.makedirs("models", exist_ok=True)
    main()