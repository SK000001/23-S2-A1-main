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
        self.sort_key, self.reversed = sort_key, True
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
        
        
    def sort_group(self):
        if self.team_mode == self.TeamMode.OPTIMISE:
            if self.sort_key == self.SortMode.HP:
                sort_func = lambda x: x.get_hp()
                
            if self.sort_key == self.SortMode.ATTACK:
                sort_func = lambda x: x.get_attack()
                
            if self.sort_key == self.SortMode.DEFENSE:
                sort_func = lambda x: x.get_defense()
                
            if self.sort_key == self.SortMode.SPEED:
                sort_func = lambda x: x.get_speed()
                
            if self.sort_key == self.SortMode.LEVEL:
                sort_func = lambda x: x.get_level()
                
            self.group = sorted(self.group, key=sort_func, reverse=self.reversed)

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
            if self.reversed:
                self.reversed = False
            else:
                self.reversed = True
            
            self.sort_group()

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
    from helpers import Flamikin, Aquariuma, Vineon, Strikeon
    from data_structures.referential_array import ArrayR
    
    team1 = MonsterTeam(
        team_mode=MonsterTeam.TeamMode.BACK,
        selection_mode=MonsterTeam.SelectionMode.PROVIDED,
        provided_monsters=ArrayR.from_list([
            Flamikin,
            Aquariuma,
            Vineon,
            Strikeon,
        ])
    )
    team2 = MonsterTeam(
        team_mode=MonsterTeam.TeamMode.FRONT,
        selection_mode=MonsterTeam.SelectionMode.PROVIDED,
        provided_monsters=ArrayR.from_list([
            Flamikin,
            Aquariuma,
            Vineon,
            Strikeon,
        ])
    )
    
    print()
    print(team1)
    print(team1.retrieve_from_team())
    print(team1.retrieve_from_team())
    print(team1.retrieve_from_team())
    print(team1.retrieve_from_team())
    
    print()
    print(team2)
    print(team2.retrieve_from_team())
    print(team2.retrieve_from_team())
    print(team2.retrieve_from_team())
    print(team2.retrieve_from_team())

