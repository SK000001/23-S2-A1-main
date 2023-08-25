from __future__ import annotations
import abc

from stats import Stats
from elements import EffectivenessCalculator, Element
from math import ceil

class MonsterBase(abc.ABC):

    def __init__(self, simple_mode=True, level:int=1) -> None:
        """
        Initialise an instance of a monster.

        :simple_mode: Whether to use the simple or complex stats of this monster
        :level: The starting level of this monster. Defaults to 1.
        """
        self.level = level
        self.simple_mode = simple_mode
        self.hp = 0
        self.hp_difference = 0
        
        self.hp = self.get_max_hp()
            
        self.original_level = level

    def get_level(self):
        """The current level of this monster instance"""
        return self.level

    def level_up(self):
        """Increase the level of this monster instance by 1"""
        self.level += 1
        self.hp = self.get_max_hp() - self.hp_difference

    def get_hp(self):
        """Get the current HP of this monster instance"""
        return self.hp

    def set_hp(self, val):
        """Set the current HP of this monster instance"""
        self.hp = val
        self.hp_difference = self.get_max_hp() - val

    def get_attack(self):
        """Get the attack of this monster instance"""
        if self.simple_mode:
            return self.get_simple_stats().get_attack()

        return self.get_complex_stats().get_attack()

    def get_defense(self):
        """Get the defense of this monster instance"""
        if self.simple_mode:
            return self.get_simple_stats().get_defense()

        return self.get_complex_stats().get_defense()

    def get_speed(self):
        """Get the speed of this monster instance"""
        if self.simple_mode:
            return self.get_simple_stats().get_speed()

        return self.get_complex_stats().get_speed()

    def get_max_hp(self):
        """Get the maximum HP of this monster instance"""
        if self.simple_mode:
            return self.get_simple_stats().get_max_hp()

        return self.get_complex_stats().get_max_hp()

    def alive(self) -> bool:
        """Whether the current monster instance is alive ( HP > 0 )"""
        if self.hp > 0:
            return True

        return False
        

    def attack(self, other: MonsterBase):
        """Attack another monster instance"""
        # Step 1: Compute attack stat vs. defense stat
        # Step 2: Apply type effectiveness
        # Step 3: Ceil to int
        # Step 4: Lose HP
        attack_stat = self.get_attack()
        defense_stat = other.get_defense()
        
        if defense_stat < attack_stat / 2:
            damage = attack_stat - defense_stat
        elif defense_stat < attack_stat:
            damage = attack_stat * 5/8 - defense_stat / 4
        else:
            damage = attack_stat / 4
        
        type1 = Element.from_string(self.get_element())
        type2 = Element.from_string(other.get_element())
        
        effectiveness = EffectivenessCalculator.get_effectiveness(type1, type2)
        effective_damage = ceil(damage * effectiveness)
        hp_lost = other.hp - effective_damage

        other.set_hp(hp_lost)

    def ready_to_evolve(self) -> bool:
        """Whether this monster is ready to evolve. See assignment spec for specific logic."""
        if self.get_evolution() != None and self.get_level() != self.original_level:
            return True

        return False

    def evolve(self) -> MonsterBase:
        """Evolve this monster instance by returning a new instance of a monster class."""
        if self.ready_to_evolve():
            evolution = self.get_evolution()(self.simple_mode, self.get_level())
            evolution.set_hp(evolution.get_max_hp() - self.hp_difference)
            
            return evolution

    def __repr__(self):
        return f"LV.{self.get_level()} {self.get_name()}, {self.get_hp()}/{self.get_max_hp()} HP"

    ### NOTE
    # Below is provided by the factory - classmethods
    # You do not need to implement them
    # And you can assume they have implementations in the above methods.

    @classmethod
    @abc.abstractmethod
    def get_name(cls) -> str:
        """Returns the name of the Monster - Same for all monsters of the same type."""
        pass

    @classmethod
    @abc.abstractmethod
    def get_description(cls) -> str:
        """Returns the description of the Monster - Same for all monsters of the same type."""
        pass

    @classmethod
    @abc.abstractmethod
    def get_evolution(cls) -> type[MonsterBase]:
        """
        Returns the class of the evolution of the Monster, if it exists.
        Same for all monsters of the same type.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def get_element(cls) -> str:
        """
        Returns the element of the Monster.
        Same for all monsters of the same type.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def can_be_spawned(cls) -> bool:
        """
        Returns whether this monster type can be spawned on a team.
        Same for all monsters of the same type.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def get_simple_stats(cls) -> Stats:
        """
        Returns the simple stats class for this monster, if it exists.
        Same for all monsters of the same type.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def get_complex_stats(cls) -> Stats:
        """
        Returns the complex stats class for this monster, if it exists.
        Same for all monsters of the same type.
        """
        pass
    
    
if __name__ == "__main__":
    from helpers import Metalhorn
    def test_leveled_stats():
        class MockedMetalhorn(Metalhorn):
            def get_max_hp(self):
                return 4 * self.get_level() + 2
        t:MonsterBase = MockedMetalhorn(simple_mode=True, level=2)
        t.set_hp(8)
        t.level_up()
        print(t.get_max_hp())
        print(t.get_hp())
        
    test_leveled_stats()