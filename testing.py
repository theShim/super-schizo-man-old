import pygame
import time

class Move:
    def __init__(self, name, sequence, cooldown=None):
        self.name = name
        self.sequence = sequence
        self.cooldown = cooldown
        self.last_execution_time = 0
        self.is_executing = False
        self.key_released = True

    def check_sequence(self, keys_pressed):
        if self.sequence and not self.is_executing and self.key_released:
            sequence_copy = self.sequence[:]  # Create a copy of the sequence list
            for key in self.sequence:
                if keys_pressed[key]:
                    sequence_copy.pop(0)  # Remove the first key from the copied sequence
                    if not sequence_copy:
                        if self.cooldown is not None:
                            self.last_execution_time = time.time()
                        self.is_executing = True
                        self.key_released = False
                        return True
                else:
                    return False
            return False

    def reset_execution(self):
        self.is_executing = False

    def release_key(self):
        self.key_released = True

class MoveManager:
    def __init__(self):
        self.moves = {}

    def add_move(self, move):
        self.moves[move.name] = move

    def execute_move(self, keys_pressed):
        for name, move in self.moves.items():
            if move.check_sequence(keys_pressed):
                print(f"Executing {move.name} move")
                # Perform actions for the move
                return True
        return False

    def reset_moves(self):
        for name, move in self.moves.items():
            move.reset_execution()

    def release_keys(self):
        for name, move in self.moves.items():
            move.release_key()

# Example usage
def main():
    pygame.init()
    screen = pygame.display.set_mode((400, 400))
    clock = pygame.time.Clock()

    # Define move sets with sequences and cooldowns
    punch_move = Move("Punch", [pygame.K_SPACE], cooldown=1.0)
    combo_move = Move("Combo", [pygame.K_a, pygame.K_d])  # No cooldown for combo move

    # Create move manager
    move_manager = MoveManager()
    move_manager.add_move(punch_move)
    move_manager.add_move(combo_move)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYUP:
                move_manager.release_keys()  # Release keys when they are released

        keys_pressed = pygame.key.get_pressed()
        if move_manager.execute_move(keys_pressed):
            # If a move is executed, pause other actions
            move_manager.reset_moves()  # Reset move execution flags
            continue

        # Regular player movement and other actions
        # Add your player movement logic here

        screen.fill((255, 255, 255))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
   