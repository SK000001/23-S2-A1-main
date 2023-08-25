from __future__ import annotations
from enum import auto
from typing import Optional, TYPE_CHECKING

from base_enum import BaseEnum
from monster_base import MonsterBase
from random_gen import RandomGen
from helpers import get_all_monsters, MonsterBaseFactory
from stats import ComplexStats, SimpleStats

from data_structures.referential_array import ArrayR

import math

if TYPE_CHECKING:
    from battle import Battle

class MonsterTeam:

    class TeamMode(BaseEnum):

        FRONT = auto()
        BACK = auto()
        OPTIMISE = auto()

    class SelectionMode(BaseEnum):

        RANDOM = auto()
        MANUAL = auto()
        PROVIDED = auto()

    class SortMode(BaseEnum):

        HP = auto()
        ATTACK = auto()
        DEFENSE = auto()
        SPEED = auto()
        LEVEL = auto()

    TEAM_LIMIT = 6

    def __init__(self, team_mode: TeamMode, selection_mode, sort_key=SortMode.HP, provided_monsters=None) -> None:
        self.group = []
        self.monsters = get_all_monsters()
        self.sort_key, self.reversed = sort_key, False
        self.lives = 2
        
        self.team_mode = team_mode
        if selection_mode == self.SelectionMode.RANDOM:
            self.select_randomly()
        elif selection_mode == self.SelectionMode.MANUAL:
            self.select_manually()
        elif selection_mode == self.SelectionMode.PROVIDED:
            self.select_provided(provided_monsters)
        else:
            raise ValueError(f"selection_mode {selection_mode} not supported.")
        
        if team_mode == self.TeamMode.OPTIMISE:
            self.sort_group()
            
        self.original = [i for i in self.group]
        
    def get_stat(self, monster1, monster2):
        if self.sort_key == self.SortMode.HP:
            return monster1.get_hp(), monster2.get_hp()
        
        if self.sort_key == self.SortMode.ATTACK:
            return monster1.get_attack(), monster2.get_attack()
        
        if self.sort_key == self.SortMode.DEFENSE:
            return monster1.get_defense(), monster2.get_defense()
            
        if self.sort_key == self.SortMode.SPEED:
            return monster1.get_speed(), monster2.get_speed()
            
        if self.sort_key == self.SortMode.LEVEL:
            return monster1.get_level(), monster2.get_level()   
        
    def sort_group(self):
        for i in range(1, len(self.group)):
            j = i-1
            
            item, next_item = self.group[i], self.group[j]
            
            if self.reversed == False:
                stat1, stat2 = self.get_stat(item, next_item)
            else:
                stat1, stat2 = self.get_stat(next_item, item)
            
            while j >= 0 and stat1 > stat2:
                self.group[j + 1] = next_item
                j -= 1
                next_item = self.group[j]
                
                if self.reversed == False:
                    stat1, stat2 = self.get_stat(item, next_item)
                else:
                    stat1, stat2 = self.get_stat(next_item, item)

            self.group[j + 1] = item

    def add_to_team(self, monster: MonsterBase):
        if self.team_mode == self.TeamMode.FRONT:
            self.group.insert(0, monster)
            return
        
        self.group.append(monster)

        if self.team_mode == self.TeamMode.OPTIMISE:
            self.sort_group()
            return

    def retrieve_from_team(self) -> MonsterBase:
        return self.group.pop(0)

    def special(self) -> None:
        if self.team_mode == self.TeamMode.FRONT:
            self.group = self.group[:3][::-1] + self.group[3:]
            return
        
        if self.team_mode == self.TeamMode.BACK:
            l = len(self.group)
            mid = []
            
            if l % 2 != 0:
                mid = [self.group[l//2]]
            
            self.group = self.group[math.ceil(l/2):][::-1] + mid + self.group[:math.floor(l/2)]
            return
        
        if self.team_mode == self.TeamMode.OPTIMISE:
            self.group = self.group[::-1]
            
            if self.reversed == True:
                self.reversed = False
            else:
                self.reversed = True

    def regenerate_team(self) -> None:
        x = []
        for i in self.original:
            x.append(i)
            
        self.group = x
        
        for i in self.group:
            i.level = i.original_level
            i.set_hp(i.get_max_hp())

    def select_randomly(self):
        team_size = RandomGen.randint(1, self.TEAM_LIMIT)
        monsters = get_all_monsters()
        n_spawnable = 0
        for x in range(len(self.monsters)):
            if self.monsters[x].can_be_spawned():
                n_spawnable += 1

        for _ in range(team_size):
            spawner_index = RandomGen.randint(0, n_spawnable-1)
            cur_index = -1
            for x in range(len(self.monsters)):
                if self.monsters[x].can_be_spawned():
                    cur_index += 1
                    if cur_index == spawner_index:
                        # Spawn this monster
                        self.add_to_team(self.monsters[x]())
                        break
            else:
                raise ValueError("Spawning logic failed.")

    def select_manually(self):
        """
        Prompt the user for input on selecting the team.
        Any invalid input should have the code prompt the user again.

        First input: Team size. Single integer
        For _ in range(team size):
            Next input: Prompt selection of a Monster class.
                * Should take a single input, asking for an integer.
                    This integer corresponds to an index (1-indexed) of the helpers method
                    get_all_monsters()
                * If invalid of monster is not spawnable, should ask again.

        Add these monsters to the team in the same order input was provided. Example interaction:

        How many monsters are there? 2
        MONSTERS Are:
        1: Flamikin [✔️]
        2: Infernoth [❌]
        3: Infernox [❌]
        4: Aquariuma [✔️]
        5: Marititan [❌]
        6: Leviatitan [❌]
        7: Vineon [✔️]
        8: Treetower [❌]
        9: Treemendous [❌]
        10: Rockodile [✔️]
        11: Stonemountain [❌]
        12: Gustwing [✔️]
        13: Stormeagle [❌]
        14: Frostbite [✔️]
        15: Blizzarus [❌]
        16: Thundrake [✔️]
        17: Thunderdrake [❌]
        18: Shadowcat [✔️]
        19: Nightpanther [❌]
        20: Mystifly [✔️]
        21: Telekite [❌]
        22: Metalhorn [✔️]
        23: Ironclad [❌]
        24: Normake [❌]
        25: Strikeon [✔️]
        26: Venomcoil [✔️]
        27: Pythondra [✔️]
        28: Constriclaw [✔️]
        29: Shockserpent [✔️]
        30: Driftsnake [✔️]
        31: Aquanake [✔️]
        32: Flameserpent [✔️]
        33: Leafadder [✔️]
        34: Iceviper [✔️]
        35: Rockpython [✔️]
        36: Soundcobra [✔️]
        37: Psychosnake [✔️]
        38: Groundviper [✔️]
        39: Faeboa [✔️]
        40: Bugrattler [✔️]
        41: Darkadder [✔️]
        Which monster are you spawning? 38
        MONSTERS Are:
        1: Flamikin [✔️]
        2: Infernoth [❌]
        3: Infernox [❌]
        4: Aquariuma [✔️]
        5: Marititan [❌]
        6: Leviatitan [❌]
        7: Vineon [✔️]
        8: Treetower [❌]
        9: Treemendous [❌]
        10: Rockodile [✔️]
        11: Stonemountain [❌]
        12: Gustwing [✔️]
        13: Stormeagle [❌]
        14: Frostbite [✔️]
        15: Blizzarus [❌]
        16: Thundrake [✔️]
        17: Thunderdrake [❌]
        18: Shadowcat [✔️]
        19: Nightpanther [❌]
        20: Mystifly [✔️]
        21: Telekite [❌]
        22: Metalhorn [✔️]
        23: Ironclad [❌]
        24: Normake [❌]
        25: Strikeon [✔️]
        26: Venomcoil [✔️]
        27: Pythondra [✔️]
        28: Constriclaw [✔️]
        29: Shockserpent [✔️]
        30: Driftsnake [✔️]
        31: Aquanake [✔️]
        32: Flameserpent [✔️]
        33: Leafadder [✔️]
        34: Iceviper [✔️]
        35: Rockpython [✔️]
        36: Soundcobra [✔️]
        37: Psychosnake [✔️]
        38: Groundviper [✔️]
        39: Faeboa [✔️]
        40: Bugrattler [✔️]
        41: Darkadder [✔️]
        Which monster are you spawning? 2
        This monster cannot be spawned.
        Which monster are you spawning? 1
        """
        while True:
            team_size = int(input("How many monsters are there? "))
            
            if team_size > 0 and team_size < 7:
                
                for _ in range(team_size):
                    
                    while True:
                        print("MONSTERS are:")
                        for i in range(len(self.monsters)):
                            print(i+1, self.monsters[i].get_name(), "[✔️]" if self.monsters[i].can_be_spawned() else "[❌]")
                            
                        spawn = int(input("Which monster are you spawning? "))
                        
                        if self.monsters[spawn-1].can_be_spawned():
                            self.add_to_team(self.monsters[spawn-1]())
                            break
                    
                break
            
            print("Please provide a number between 1 and 6.")
        

    def select_provided(self, provided_monsters:Optional[ArrayR[type[MonsterBase]]]=None):
        """
        Generates a team based on a list of already provided monster classes.

        While the type hint imples the argument can be none, this method should never be called without the list.
        Monsters should be added to the team in the same order as the provided array.

        Example input:
        [Flamikin, Aquariuma, Gustwing] <- These are all classes.

        Example team if in TeamMode.FRONT:
        [Gustwing Instance, Aquariuma Instance, Flamikin Instance]
        """
        if len(provided_monsters) > 6 or len(provided_monsters) < 1:
            raise ValueError("Please provide a valid amount of monsters.")
        
        for i in provided_monsters:
            if i.can_be_spawned() == False:
                self.group = []
                raise ValueError("Please provide spawnable monster")
            
            self.add_to_team(i())
            

    def choose_action(self, currently_out: MonsterBase, enemy: MonsterBase) -> Battle.Action:
        # This is just a placeholder function that doesn't matter much for testing.
        from battle import Battle
        if currently_out.get_speed() >= enemy.get_speed() or currently_out.get_hp() >= enemy.get_hp():
            return Battle.Action.ATTACK
        return Battle.Action.SWAP
    
    def __repr__(self) -> str:
        return f"<{type(self).__name__}: {self.group}>"
    
    def __len__(self):
        return len(self.group)
            

if __name__ == "__main__":
    from helpers import Flamikin, Aquariuma, Rockodile, Thundrake
    from data_structures.referential_array import ArrayR
    
    my_monsters = ArrayR(4)
    my_monsters[0] = Flamikin   # 6 HP
    my_monsters[1] = Aquariuma  # 8 HP
    my_monsters[2] = Rockodile  # 9 HP
    my_monsters[3] = Thundrake  # 5 HP
    team = MonsterTeam(
        team_mode=MonsterTeam.TeamMode.OPTIMISE,
        selection_mode=MonsterTeam.SelectionMode.PROVIDED,
        sort_key=MonsterTeam.SortMode.HP,
        provided_monsters=my_monsters,
    )
    # Rockodile, Aquariuma, Flamikin, Thundrake
    rockodile = team.retrieve_from_team()
    aquariuma = team.retrieve_from_team()
    flamikin = team.retrieve_from_team()
    
    print(rockodile, aquariuma, flamikin, sep="\n", end="\n\n")
    # self.assertIsInstance(rockodile, Rockodile)
    # self.assertIsInstance(aquariuma, Aquariuma)
    # self.assertIsInstance(flamikin, Flamikin)

    rockodile.set_hp(2)
    flamikin.set_hp(4)
    team.add_to_team(rockodile)
    team.add_to_team(aquariuma)
    team.add_to_team(flamikin)
    # # Aquariuma, Thundrake, Flamikin, Rockodile

    team.special()
    # # Rockodile, Flamikin, Thundrake, Aquariuma
    # rockodile = team.retrieve_from_team()
    # flamikin = team.retrieve_from_team()
    # self.assertIsInstance(rockodile, Rockodile)
    # self.assertIsInstance(flamikin, Flamikin)
    print(rockodile, flamikin, sep="\n", end="\n\n")


    flamikin.set_hp(1)
    team.add_to_team(flamikin)
    team.add_to_team(rockodile)

    flamikin = team.retrieve_from_team()
    # self.assertIsInstance(flamikin, Flamikin)
    print(flamikin, end="\n\n")

    team.regenerate_team()
    # # Back to normal sort order and Rockodile, Aquariuma, Flamikin, Thundrake
    rockodile = team.retrieve_from_team()
    aquariuma = team.retrieve_from_team()
    # self.assertIsInstance(rockodile, Rockodile)
    # self.assertIsInstance(aquariuma, Aquariuma)
    # self.assertEqual(rockodile.get_hp(), 9)
    # self.assertEqual(aquariuma.get_hp(), 8)
    
    print(rockodile, aquariuma, rockodile.get_hp(), aquariuma.get_hp(), sep="\n")

