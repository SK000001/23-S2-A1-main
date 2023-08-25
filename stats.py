import abc

from data_structures.referential_array import ArrayR

class Stats(abc.ABC):

    @abc.abstractmethod
    def get_attack(self):
        pass

    @abc.abstractmethod
    def get_defense(self):
        pass

    @abc.abstractmethod
    def get_speed(self):
        pass

    @abc.abstractmethod
    def get_max_hp(self):
        pass


class SimpleStats(Stats):

    def __init__(self, attack, defense, speed, max_hp) -> None:
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.max_hp = max_hp

    def get_attack(self):
        return self.attack

    def get_defense(self):
        return self.defense

    def get_speed(self):
        return self.speed

    def get_max_hp(self):
        return self.max_hp

class ComplexStats(Stats):
    def __init__(
        self,
        attack_formula: ArrayR[str],
        defense_formula: ArrayR[str],
        speed_formula: ArrayR[str],
        max_hp_formula: ArrayR[str],
    ) -> None:
        
        self.attack_formula = attack_formula
        self.defense_formula = defense_formula
        self.speed_formula = speed_formula
        self.max_hp_formula = max_hp_formula
        
    def compute_pos(self, exp: ArrayR[str], level: int):
        stack = []
        
        for i in range(exp.__len__()):
            val = exp.__getitem__(i)
            
            if val not in ["middle", "power", "sqrt", "+", "-", "*", "/", "level"]:
                stack.append(int(val))
                
            else:
                if val == "level":
                    stack.append(level)
                        
                if val == "sqrt":
                    stack.append(stack.pop() ** 0.5)
                        
                if val == "middle":
                    if i == exp.__len__()-1:
                        stack = [sorted(stack)[len(stack)//2]]
                        
                    else:
                        data = sorted(stack[1:i])
                        stack = [stack[0]] + [data[len(data)//2]]
                        
                if val in ["+", "-", "*", "/", "power"]:
                    left = stack.pop()
                    right = stack.pop()
                    
                    if val == "power":
                        stack.append(right ** left)
                        
                    if val == "+":
                        stack.append(right + left)
                    
                    if val == "-":
                        stack.append(right - left)
                        
                    if val == "*":
                        stack.append(right * left)
                        
                    if val == "/":
                        stack.append(right / left)
                    
        return stack.pop()
                
                
    def get_attack(self, level: int):
        return self.compute_pos(self.attack_formula, level)

    def get_defense(self, level: int):
        return self.compute_pos(self.defense_formula, level)

    def get_speed(self, level: int):
        return self.compute_pos(self.speed_formula, level)

    def get_max_hp(self, level: int):
        return self.compute_pos(self.max_hp_formula, level)