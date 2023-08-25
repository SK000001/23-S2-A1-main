from __future__ import annotations

from random_gen import RandomGen
from team import MonsterTeam
from battle import Battle

from elements import Element

from data_structures.referential_array import ArrayR

class BattleTower:

    MIN_LIVES = 2
    MAX_LIVES = 10

    def __init__(self, battle: Battle|None=None) -> None:
        self.battle = battle or Battle(verbosity=0)
        self.my_team = None
        self.enemy_teams = None
        self.current_enemy_index = 0

    def set_my_team(self, team: MonsterTeam) -> None:
        # Generate the team lives here too.
        self.my_team = team
        self.my_team.lives = RandomGen.randint(self.MIN_LIVES, self.MAX_LIVES)

    def generate_teams(self, n: int) -> None:
        self.enemy_teams = ArrayR(n)
        
        for i in range(n):
            enemy = MonsterTeam(MonsterTeam.TeamMode.BACK, MonsterTeam.SelectionMode.RANDOM)
            enemy.lives = RandomGen.randint(self.MIN_LIVES, self.MAX_LIVES)
            self.enemy_teams[i] = enemy

    def battles_remaining(self) -> bool:
        return (self.my_team.lives > 0 and any(enemy.lives > 0 for enemy in self.enemy_teams)) and len(self.enemy_teams) > self.current_enemy_index

    def next_battle(self) -> tuple[Battle.Result, MonsterTeam, MonsterTeam, int, int]:
        if not self.battles_remaining():
            return Battle.Result.DRAW, self.my_team, None, self.my_team.lives, 0
        
        team1 = self.my_team
        team2 = self.enemy_teams[self.current_enemy_index]
        
        battle_result = self.battle.battle(team1=team1, team2=team2)
        
        self.current_enemy_index += 1
        
        if battle_result == Battle.Result.TEAM1:
            team2.lives -= 1
        elif battle_result == Battle.Result.TEAM2:
            team1.lives -= 1
        elif battle_result == Battle.Result.DRAW:
            team1.lives -= 1
            team2.lives -= 1
            
        team1.regenerate_team()
        team2.regenerate_team()
        
        return battle_result, team1, team2, team1.lives, team2.lives
        

    def out_of_meta(self) -> ArrayR[Element]:
        if not self.battles_remaining() or self.current_enemy_index == 0:
            return ArrayR.from_list([])
        
        previous_team = self.enemy_teams[self.current_enemy_index - 1].group
        upcoming_team = self.enemy_teams[self.current_enemy_index].group
        
        previous_team_elements = [Element.from_string(i.get_element()) for i in previous_team]
        upcoming_team_elements = [Element.from_string(i.get_element()) for i in upcoming_team]
        player_team_elements = [Element.from_string(i.get_element()) for i in self.my_team.group]
        
        for i in upcoming_team_elements:
            if i not in player_team_elements:
                player_team_elements.append(i)
        
        metas = []
        
        for i in previous_team_elements:
            if i not in player_team_elements:
                metas.append(i)
                
        return ArrayR.from_list(metas)

    def sort_by_lives(self):
        # 1054 ONLY
        raise NotImplementedError

def tournament_balanced(tournament_array: ArrayR[str]):
    # 1054 ONLY
    raise NotImplementedError

if __name__ == "__main__":
    from helpers import Faeboa

    RandomGen.set_seed(123456789)
    bt = BattleTower(Battle(verbosity=0))
    bt.set_my_team(MonsterTeam(
        team_mode=MonsterTeam.TeamMode.BACK,
        selection_mode=MonsterTeam.SelectionMode.PROVIDED,
        provided_monsters=ArrayR.from_list([Faeboa])
    ))
    bt.generate_teams(3)
    
    # print(bt.out_of_meta().to_list())
    result, t1, t2, l1, l2 = bt.next_battle()
    
    # print(bt.out_of_meta().to_list())
    result, t1, t2, l1, l2 = bt.next_battle()
    
    print(bt.out_of_meta().to_list())
    
        # The following teams should have been generated:
        # 1 (7 lives): Strikeon, Faeboa, Shockserpent, Gustwing, Vineon, Pythondra
            # Fighting, Fairy, Electricity, Flying, Grass, Dragon
        # 2 (5 lives): Iceviper, Thundrake, Groundviper, Iceviper, Metalhorn
            # Ice, Electric, Ground, Steel
        # 3 (3 lives): Strikeon
            # Fighting

        # When no games have been played, noone is outside of the meta.
        # self.assertListEqual(bt.out_of_meta().to_list(), [])
        
        # result, t1, t2, l1, l2 = bt.next_battle()
        # # After the first game, Fighting, Flying, Grass and Dragon are no longer in the meta.
        # # Electric & Fairy are still present in the battle between the two.
        # self.assertListEqual(bt.out_of_meta().to_list(), [Element.GRASS, Element.DRAGON, Element.FIGHTING, Element.FLYING])
        
        # result, t1, t2, l1, l2 = bt.next_battle()
        # # After the second game, Flying, Grass, Dragon, Ice, Electric, Ground, Steel are no longer present.
        # self.assertListEqual(bt.out_of_meta().to_list(), [Element.GRASS, Element.DRAGON, Element.ELECTRIC, Element.FLYING, Element.GROUND, Element.ICE, Element.STEEL])
        # result, t1, t2, l1, l2 = bt.next_battle()
        # # After the third game, We are just missing Ice, Ground and Steel.
        # self.assertListEqual(bt.out_of_meta().to_list(), [Element.GROUND, Element.ICE, Element.STEEL])
        # result, t1, t2, l1, l2 = bt.next_battle()
        # # After the fourth game, We are back to missing Grass, Dragon, Fighting and Flying
        # self.assertListEqual(bt.out_of_meta().to_list(), [Element.GRASS, Element.DRAGON, Element.FIGHTING, Element.FLYING])