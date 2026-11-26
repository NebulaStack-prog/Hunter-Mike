import unittest
import Industrial_Zero as game

class GameTests(unittest.TestCase):
    def test_player_initial_position(self):
        p = game.Player(100, 200)
        self.assertEqual(p.rect.topleft, (100, 200))
        self.assertFalse(p.keycard)
        self.assertFalse(p.power_on)

    def test_grounded_jump(self):
        p = game.Player(100, 200)
        p.on_ground = True
        p.jump()
        self.assertEqual(p.vy, -game.JUMP_SPEED)
        self.assertFalse(p.on_ground)

    def test_airborne_jump(self):
        p = game.Player(100, 200)
        p.jump()
        self.assertEqual(p.vy, 0)

    def test_level_geometry(self):
        self.assertTrue(game.PLATFORMS)
        for rect in game.PLATFORMS:
            self.assertGreater(rect.width, 0)
            self.assertGreater(rect.height, 0)
            self.assertGreaterEqual(rect.left, 0)
            self.assertLessEqual(rect.right, game.WORLD_W)
