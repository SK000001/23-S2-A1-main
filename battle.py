from __future__ import annotations
from enum import auto
from typing import Optional

from base_enum import BaseEnum
from team import MonsterTeam


class Battle:

    class Action(BaseEnum):
        ATTACK = auto()
        SWAP = auto()
        SPECIAL = auto()

    class Result(BaseEnum):
        TEAM1 = auto()
        TEAM2 = auto()
        DRAW = auto()

    def __init__(self, verbosity=0) -> None:
        self.verbosity = verbosity
        self.action1 = None
        self.action2 = None 
        
    def both_alive(self):
        self.out1.set_hp(self.out1.get_hp() - 1)
        self.out2.set_hp(self.out2.get_hp() - 1)
        
        alive1, alive2 = self.out1.alive(), self.out2.alive()
                
        if not alive1:
            if alive2:
                self.out2.level_up()
                
                if self.out2.ready_to_evolve():
                    self.out2 = self.out2.evolve()
            
            if self.team1.__len__() > 0:
                self.out1 = self.team1.retrieve_from_team()
            else:
                return self.Result.TEAM2
                
        if not alive2:
            if alive1:
                self.out1.level_up()
                
                if self.out1.ready_to_evolve():
                    self.out1 = self.out1.evolve()
                
            if self.team2.__len__() > 0:
                self.out2 = self.team2.retrieve_from_team()
            else:
                return self.Result.TEAM1
                
        return

    def process_turn(self) -> Optional[Battle.Result]:
        """
        Process a single turn of the battle. Should:
        * process actions chosen by each team
        * level and evolve monsters
        * remove fainted monsters and retrieve new ones.
        * return the battle result if completed.
        """
        action1 = MonsterTeam.choose_action(self, currently_out=self.out1, enemy=self.out2)
        action2 = MonsterTeam.choose_action(self, currently_out=self.out2, enemy=self.out1)
        
        if action1 == self.Action.SPECIAL:
            self.team1.add_to_team(self.out1)
            self.team1.special()
            self.out1 = self.team1.retrieve_from_team()
            action1 = None
        
        if action2 == self.Action.SPECIAL:
            self.team2.add_to_team(self.out2)
            self.team2.special()
            self.out2 = self.team2.retrieve_from_team()
            action2 = None
            
        if action1 == self.Action.SWAP:
            self.team1.add_to_team(self.out1)
            self.out1 = self.team1.retrieve_from_team()
            action1 = None
            
        if action2 == self.Action.SWAP:
            self.team2.add_to_team(self.out2)
            self.out2 = self.team2.retrieve_from_team()
            action2 = None
            
        if (action1 == None) and (action2 == None):
            return
            
        out1_speed = self.out1.get_speed()
        out2_speed = self.out2.get_speed()
        
        alive1, alive2 = True, True
            
        if out1_speed == out2_speed:
            if action1 != None:
                self.out1.attack(self.out2)
                
            if action2 != None:
                self.out2.attack(self.out1)
                
            if self.out1.alive() and self.out2.alive():
                self.out1.set_hp(self.out1.get_hp() - 1)
                self.out2.set_hp(self.out2.get_hp() - 1)
                
            alive1, alive2 = self.out1.alive(), self.out2.alive()
                
            if not alive1:
                if alive2:
                    self.out2.level_up()
                    
                    if self.out2.ready_to_evolve():
                        self.out2 = self.out2.evolve()
                
                if self.team1.__len__() > 0:
                    self.out1 = self.team1.retrieve_from_team()
                else:
                    return self.Result.TEAM2
                    
            if not alive2:
                if alive1:
                    self.out1.level_up()
                    
                    if self.out1.ready_to_evolve():
                        self.out1 = self.out1.evolve()
                    
                if self.team2.__len__() > 0:
                    self.out2 = self.team2.retrieve_from_team()
                else:
                    return self.Result.TEAM1
                    
            return
            
        if out1_speed > out2_speed:
            if action1 != None:
                self.out1.attack(self.out2)
                
                if not self.out2.alive():
                    self.out1.level_up()
                    
                    if self.out1.ready_to_evolve():
                        self.out1 = self.out1.evolve()
                        
                    if self.team2.__len__() > 0:
                        self.out2 = self.team2.retrieve_from_team()
                        return

                    return self.Result.TEAM1
                    
            if action2 != None:
                self.out2.attack(self.out1)
                
                if not self.out1.alive():
                    self.out2.level_up()
                    
                    if self.out2.ready_to_evolve():
                        self.out2 = self.out2.evolve()
                    
                    if self.team1.__len__() > 0:
                        self.out1 = self.team1.retrieve_from_team()
                        return
   
                    return self.Result.TEAM2 
                
            return self.both_alive()     
        
        if out2_speed > out1_speed:
            alive1, alive2 = True, True
            
            if action2 != None:
                self.out2.attack(self.out1)
                
                if not self.out1.alive():
                    self.out2.level_up()
                    
                    if self.out2.ready_to_evolve():
                        self.out2 = self.out2.evolve()
                    
                    if self.team1.__len__() > 0:
                        self.out1 = self.team1.retrieve_from_team()
                        return
                   
                    return self.Result.TEAM2
                    
            if action1 != None:
                self.out1.attack(self.out2) # here add action None
                
                if not self.out2.alive():
                    self.out1.level_up()
                    
                    if self.out1.ready_to_evolve():
                        self.out1 = self.out1.evolve()
                        
                    if self.team2.__len__() > 0:
                        self.out2 = self.team2.retrieve_from_team()
                        return

                    return self.Result.TEAM1
                
            return self.both_alive()
                
  

    def battle(self, team1: MonsterTeam, team2: MonsterTeam) -> Battle.Result:
        if self.verbosity > 0:
            print(f"Team 1: {team1} vs. Team 2: {team2}")
        # Add any pregame logic here.
        self.turn_number = 0
        self.team1 = team1
        self.team2 = team2
        self.out1 = team1.retrieve_from_team()
        self.out2 = team2.retrieve_from_team()

        result = None
        i = 0
        while result is None:
            if (not self.out1.alive() and self.team1.__len__() == 0) and (not self.out1.alive() and self.team1.__len__() == 0):
                return self.Result.DRAW
            
            if (not self.out1.alive() and self.team1.__len__() == 0):
                return self.Result.TEAM2
        
            if (not self.out2.alive() and self.team2.__len__() == 0):
                return self.Result.TEAM1
            
            # print("\n\n**********************************************************")
            print(f"{self.out1} vs {self.out2}")
            # print("**********************************************************\n\n")
            
            result = self.process_turn()

            # i += 1
        # Add any postgame logic here.
        return result


if __name__ == "__main__":
    # t1 = MonsterTeam(MonsterTeam.TeamMode.BACK, MonsterTeam.SelectionMode.RANDOM)
    # t2 = MonsterTeam(MonsterTeam.TeamMode.BACK, MonsterTeam.SelectionMode.RANDOM)
    # b = Battle(verbosity=3)
    # print(b.battle(t1, t2))
    from helpers import Flamikin, Aquariuma, Vineon, Strikeon
    from data_structures.referential_array import ArrayR
    
    b = Battle(verbosity=3)
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
    res = b.battle(team1, team2)
    print(res)