import csv
import json
import os
from json import JSONDecodeError
import pprint
from typing import Dict, Any
import random
import uuid
from datetime import date


def load_all_json_files():
    """Imports all JSON files into a dictionary for reference"""
    json_references = {}
    path_to_json = '../JSONstuff/'
    json_file_folders = [pos_json for pos_json in os.listdir(path_to_json)]
    for folder in json_file_folders:
        json_files = [pos_json for pos_json in os.listdir(path_to_json + folder + '/') if pos_json.endswith('.json')]
        for file in json_files:
            try:
                with open(path_to_json + folder + '/' + file) as json_file:
                    json_references.update({file[:-5]: json.load(json_file)})
            except JSONDecodeError as err:
                pass
                # print(file + ' had a problem! ' + err.msg)
    # Writes a file with every JSON file combined into one dictionary
    with open('JSON_data_files_combined.json', 'w') as outfile:
        json.dump(json_references, outfile, indent=4)
    # pprint.pprint(json_references, indent=4) # For testing pretty print

    return json_references


class Attack:

    def __init__(self, weapon, ammo_type, damage, shots, hit_percent, attack_number):
        self.weapon = weapon
        self.ammo_type = ammo_type
        self.damage = damage
        self.shots = shots
        self.hit_percent = hit_percent
        self.attack_number = attack_number
        self.isHit = 0
        self.target_body_part = None
        self.target_damage_taken = 0
        self.round = 0
        self.turn = 0
        self.attacking_mechdef_id = None
        self.defending_mechdef_id = None
        self.battle_id = None
        self.battle_date = None


class Mech:

    def __init__(self, name, mechdef_id):
        self.name = name
        self.round = 0
        self.turn = 0
        self.battle_id = None
        self.battle_date = None
        self.mechdef_id = mechdef_id
        # with open('../JSONstuff/mech/mechdef_atlas_AS7-D.json') as json_file:
        with open('../JSONstuff/mech/' + mechdef_id + '.json') as json_file:
            self.mech_data = json.load(json_file)
        self.isLeftLegDestroyed = 0
        self.isRightLegDestroyed = 0
        self.isHeadDestroyed = 0
        self.isCenterTorsoDestroyed = 0
        self.isLeftTorsoDestroyed = 0
        self.isRightTorsoDestroyed = 0
        self.isLeftArmDestroyed = 0
        self.isRightArmDestroyed = 0
        self.isLoser = 0
        for inventory in self.mech_data["inventory"]:
            weapon_ammo_capacity = 0
            weapon_ammo_type = ''
            if inventory["DamageLevel"] == "Functional" and inventory["ComponentDefType"] == "Weapon":
                weapon_ammo_type = json_reference[inventory["ComponentDefID"]]["AmmoCategory"]
                for inventory2 in self.mech_data["inventory"]:
                    weapon_ammo_type2 = ""
                    if inventory2["DamageLevel"] == "Functional" and inventory2["ComponentDefType"] == "AmmunitionBox":
                        weapon_ammo_type2 = json_reference[inventory2["ComponentDefID"]]["Description"]["Model"]
                        # print(weapon_ammo_type + " " + weapon_ammo_type2)
                        if weapon_ammo_type2 != 'NotSet' and weapon_ammo_type == weapon_ammo_type2:
                            # print(weapon_ammo_type + " " + weapon_ammo_type2)
                            weapon_ammo_capacity += json_reference["Ammo_AmmunitionBox_Generic_" + weapon_ammo_type][
                                "Capacity"]
                    if inventory2["DamageLevel"] == "Functional" and inventory2["ComponentDefType"] == "Weapon":
                        weapon_ammo_type2 = json_reference[inventory2["ComponentDefID"]]["AmmoCategory"]
                        if weapon_ammo_type2 == "Flamer" and weapon_ammo_type == weapon_ammo_type2:
                            weapon_ammo_type2 = json_reference[inventory2["ComponentDefID"]]["AmmoCategory"]
                            weapon_ammo_capacity += json_reference["Ammo_AmmunitionBox_Generic_" + weapon_ammo_type2][
                                "Capacity"]
                        # "AmmoCategory": "Flamer"
                        # print(weapon_ammo_type + " " + weapon_ammo_type2 + " " + str(weapon_ammo_capacity))
            if weapon_ammo_capacity != 0:
                inventory.update({"RemainingAmmo": weapon_ammo_capacity})
            elif weapon_ammo_type == 'NotSet':
                inventory.update({"RemainingAmmo": 100})
            elif weapon_ammo_type == 'Flamer':
                inventory.update(
                    {"RemainingAmmo": json_reference["Ammo_AmmunitionBox_Generic_" + weapon_ammo_type]["Capacity"]})


class Battle:

    def __init__(self, mech_num1, mech_num2, json_files_dict):
        self.mech1 = mech_num1
        self.mech2 = mech_num2
        self.json = json_files_dict
        self.attack_history = []
        self.battle_id = uuid.uuid1().hex
        self.battle_date = date.today()

    def start_battle(self):
        mech1.battle_id = self.battle_id
        mech2.battle_id = self.battle_id
        mech1.battle_date = self.battle_date
        mech2.battle_date = self.battle_date
        battle_start_message = "And now for an exciting battle between {} and {}! {} makes the first move!"
        whose_turn_message = "It is now {}'s turn!"
        print(battle_start_message.format(self.mech1.name, self.mech2.name, self.mech1.name))
        isBattleOver = 0
        current_round = 1
        while isBattleOver == 0:
            print()
            print(whose_turn_message.format(self.mech1.name))
            mech1.round = current_round
            mech2.round = current_round
            mech1.turn = 1
            mech2.turn = 1
            self.take_damage(mech2, self.attack_mech(mech1))
            isBattleOver = self.is_battle_over(mech2)
            if isBattleOver == 0:
                print()
                print(whose_turn_message.format(self.mech2.name))
                mech1.turn = 2
                mech2.turn = 2
                self.take_damage(mech1, self.attack_mech(mech2))
                isBattleOver = self.is_battle_over(mech1)
                current_round += 1
        if mech1.isLoser == 1:
            print(mech2.name + " is the winner!")
        elif mech2.isLoser == 1:
            print(mech1.name + " is the winner!")
        self.after_battle()

    def is_battle_over(self, mech):
        if mech.isLeftLegDestroyed == 1 and mech.isRightLegDestroyed == 1:
            print("Both Legs Destroyed! Battle Over!")
            mech.isLoser = 1
            return 1
        elif mech.isCenterTorsoDestroyed == 1:
            print("Center Torso Destroyed! Battle Over!")
            mech.isLoser = 1
            return 1
        elif mech.isHeadDestroyed == 1:
            print("Head Destroyed! Battle Over!")
            mech.isLoser = 1
            return 1
        else:
            return 0

    def attack_mech(self, mech):
        """List attacks available, prompts user for a choice, and returns attacks as a list"""
        attacks = []
        attack_count_array = []
        final_attacks_selected = []
        print("____________________________________________________")
        print("     WEAPON              AMMO      DMG        HIT%")
        print("____________________________________________________")
        count = 1
        # Creates a list of all available weapon attacks
        for inventory in mech.mech_data["inventory"]:
            if inventory["DamageLevel"] == "Functional" and inventory["ComponentDefType"] == "Weapon":
                # print(inventory["ComponentDefID"])
                weapon_name = json_reference[inventory["ComponentDefID"]]["Description"]["UIName"]
                weapon_damage_per_shot = json_reference[inventory["ComponentDefID"]]["Damage"]
                weapon_shots = json_reference[inventory["ComponentDefID"]]["ShotsWhenFired"]
                if weapon_shots > 1:
                    weapon_damage_display = str(weapon_damage_per_shot) + " (x" + str(weapon_shots) + ")"
                else:
                    weapon_damage_display = str(weapon_damage_per_shot)
                weapon_ammo_type = json_reference[inventory["ComponentDefID"]]["AmmoCategory"]
                if weapon_ammo_type == 'NotSet':
                    weapon_ammo_capacity = "---"
                else:
                    weapon_ammo_capacity = inventory["RemainingAmmo"]
                # Substitute Constants for Weapon Accuracy at some point
                weapon_accuracy = 0.65  # 0.55
                if weapon_ammo_type == 'NotSet' or (inventory["RemainingAmmo"] > 0 and weapon_ammo_type != 'NotSet'):
                    print(str(count) + ": " + (3 - len(str(count))) * " " +
                          weapon_name + ((20 - len(weapon_name)) * " ") +
                          str(weapon_ammo_capacity) + ((10 - len(str(weapon_ammo_capacity))) * " ") +
                          weapon_damage_display + ((11 - len(weapon_damage_display)) * " ") +
                          str(round(weapon_accuracy * 100)) + "%")
                    attacks.append(Attack(weapon=weapon_name,
                                          ammo_type=weapon_ammo_type,
                                          damage=weapon_damage_per_shot,
                                          shots=weapon_shots,
                                          hit_percent=weapon_accuracy,
                                          attack_number=count
                                          )
                                   )
                    attack_count_array.append(count)
                    count += 1
        # Prompts the user for attack selection and validates it
        i = 0
        while i == 0:
            # Asking for user input
            # attack_selection = input(
            #     'Enter the numbers of the weapons you want to fire, separated by commas(ex. "1,3,6"): ')
            # attack_selection = attack_selection.split(",")

            # Generating random attacks
            attack_selection = []
            for _ in attack_count_array:
                attack_selection.append(str(random.choice(attack_count_array)))
            # print(attack_selection)
            # attack_selection = ['1', '2']
            # attack_selection = ['1']
            attack_selection_array = []
            try:
                for x in attack_selection:
                    attack_selection_array.append(int(x.strip()))
                if not attack_count_array.__len__():
                    i = 1
                    print(mech.name + " is out of weapons and rams the opponent!")
                    melee_damage = json_reference[mech.mech_data["ChassisID"]]["MeleeDamage"]
                    # print(melee_damage)
                    a = Attack(weapon="Melee Attack",
                               ammo_type="Physical",
                               damage=melee_damage,
                               shots=1,
                               hit_percent=0.85,
                               attack_number=1)
                    a.round = mech.round
                    a.turn = mech.turn
                    a.attacking_mechdef_id = mech.mechdef_id
                    a.battle_id = mech.battle_id
                    a.battle_date = mech.battle_date
                    final_attacks_selected.append(a)
                    return final_attacks_selected
                elif all(x in attack_count_array for x in attack_selection_array):
                    i = 1
                else:
                    print("Invalid input! Try again!")
                    print(attack_selection_array)
                    print(attack_selection)
                    print(attack_count_array)
                    i = 1
            except ValueError:
                print("Invalid input! Try again!")
            # figure out checking if the selection is valid
            # print(attack_selection)
            # print(attack_selection_array)
            # print(attack_count_array)
            # print(i)

        for a in attacks:
            if a.attack_number in attack_selection_array:
                # Calculates if a weapon is out of ammo after an attack
                for inventory in mech.mech_data["inventory"]:
                    if inventory["DamageLevel"] == "Functional" and inventory["ComponentDefType"] == "Weapon":
                        weapon_ammo_type = json_reference[inventory["ComponentDefID"]]["AmmoCategory"]
                        if a.ammo_type == weapon_ammo_type and weapon_ammo_type != 'NotSet':
                            # Deducts ammo used
                            inventory["RemainingAmmo"] -= a.shots
                            # Should only run once
                            if inventory["RemainingAmmo"] < 0:
                                # Attack uses remaining ammo, not number of shots
                                a.shots += inventory["RemainingAmmo"]
                                # Set all Remaining ammo numbers to zero for that ammo type
                                for inventory2 in mech.mech_data["inventory"]:
                                    if inventory2["DamageLevel"] == "Functional" and inventory2[
                                        "ComponentDefType"] == "Weapon":
                                        weapon_ammo_type2 = json_reference[inventory2["ComponentDefID"]]["AmmoCategory"]
                                        if a.ammo_type == weapon_ammo_type2 and weapon_ammo_type2 != 'NotSet':
                                            inventory2["RemainingAmmo"] = 0
                                # Set later attacks to use 0 shots
                                for b in attacks:
                                    if a.attack_number < b.attack_number and a.ammo_type == b.ammo_type:
                                        b.shots = 0
                                print(a.weapon + " is out of ammo and can no longer be used!")
                            elif inventory["RemainingAmmo"] == 0:
                                print(a.weapon + " is out of ammo and can no longer be used!")
                # Records attributes of attacks to generate history
                a.round = mech.round
                a.turn = mech.turn
                a.attacking_mechdef_id = mech.mechdef_id
                a.battle_id = mech.battle_id
                a.battle_date = mech.battle_date
                final_attacks_selected.append(a)

        return final_attacks_selected

    def take_damage(self, mech, attacks):
        # Calculate a hit or miss to a random body part
        for attack in attacks:
            mech_location = self.determine_target_body_part(mech)
            attack_damage = 0
            for shot in range(0, attack.shots):
                attack_try = random.randint(1, 100) / 100
                if attack_try <= attack.hit_percent:
                    if attack.isHit == 0:
                        attack.isHit = 1
                    for location in mech.mech_data["Locations"]:
                        if location["Location"] == mech_location:
                            # Actual Damage Taking
                            location["CurrentArmor"] -= attack.isHit * attack.damage
                            attack_damage += attack.isHit * attack.damage
                            # print(location["CurrentArmor"])
            if attack.isHit == 1:
                print(mech_location + " was hit for " + str(attack_damage) + " damage by " + attack.weapon + "!")
                attack.target_damage_taken = attack_damage
            else:
                print(mech_location + " missed!")
            # Records attributes of attacks to history
            attack.defending_mechdef_id = mech.mechdef_id
            attack.target_body_part = mech_location
            self.attack_history.append(attack)
        # Checks if body parts are destroyed and passes along extra damage to the torsos
        damage_to_left_torso = 0
        damage_to_right_torso = 0
        damage_to_center_torso = 0
        # Legs and Arms first
        for location in mech.mech_data["Locations"]:
            if location["Location"] == 'LeftLeg' and location["DamageLevel"] == "Functional" and location[
                "CurrentArmor"] <= 0:
                location["CurrentInternalStructure"] += location["CurrentArmor"]
                location["CurrentArmor"] = 0
                if location["CurrentInternalStructure"] <= 0:
                    location["DamageLevel"] = "Destroyed"
                    mech.isLeftLegDestroyed = 1
                    print("Left Leg Destroyed!")
            if location["Location"] == 'RightLeg' and location["DamageLevel"] == "Functional" and location[
                "CurrentArmor"] <= 0:
                location["CurrentInternalStructure"] += location["CurrentArmor"]
                location["CurrentArmor"] = 0
                if location["CurrentInternalStructure"] <= 0:
                    location["DamageLevel"] = "Destroyed"
                    mech.isRightLegDestroyed = 1
                    print("Right Leg Destroyed!")
            if location["Location"] == 'LeftArm' and location["DamageLevel"] == "Functional" and location[
                "CurrentArmor"] <= 0:
                location["CurrentInternalStructure"] += location["CurrentArmor"]
                location["CurrentArmor"] = 0
                if location["CurrentInternalStructure"] <= 0:
                    location["DamageLevel"] = "Destroyed"
                    mech.isLeftArmDestroyed = 1
                    damage_to_left_torso += location["CurrentInternalStructure"]
                    print("Left Arm Destroyed!")
            if location["Location"] == 'RightArm' and location["DamageLevel"] == "Functional" and location[
                "CurrentArmor"] <= 0:
                location["CurrentInternalStructure"] += location["CurrentArmor"]
                location["CurrentArmor"] = 0
                if location["CurrentInternalStructure"] <= 0:
                    location["DamageLevel"] = "Destroyed"
                    mech.isRightArmDestroyed = 1
                    damage_to_right_torso += location["CurrentInternalStructure"]
                    print("Right Arm Destroyed!")
        # Left and Right Torsos second
        for location in mech.mech_data["Locations"]:
            if location["Location"] == 'LeftTorso' and location["DamageLevel"] == "Functional" \
                    and location["CurrentArmor"] + damage_to_left_torso <= 0:
                location["CurrentInternalStructure"] += location["CurrentArmor"] + damage_to_left_torso
                location["CurrentArmor"] = 0
                if location["CurrentInternalStructure"] <= 0:
                    location["DamageLevel"] = "Destroyed"
                    damage_to_center_torso += location["CurrentInternalStructure"]
                    print("Left Torso Destroyed!")
                    mech.isLeftTorsoDestroyed = 1
            if location["Location"] == 'RightTorso' and location["DamageLevel"] == "Functional" \
                    and location["CurrentArmor"] + damage_to_right_torso <= 0:
                location["CurrentInternalStructure"] += location["CurrentArmor"] + damage_to_right_torso
                location["CurrentArmor"] = 0
                if location["CurrentInternalStructure"] <= 0:
                    location["DamageLevel"] = "Destroyed"
                    damage_to_center_torso += location["CurrentInternalStructure"]
                    print("Right Torso Destroyed!")
                    mech.isRightTorsoDestroyed = 1
        # Marks the arms destroyed of either torso is destroyed first
        for location in mech.mech_data["Locations"]:
            if location["Location"] == "LeftArm":
                if mech.isLeftTorsoDestroyed == 1 and mech.isLeftArmDestroyed == 0:
                    print("Left Arm destroyed due to Left Torso being destroyed")
                    mech.isLeftArmDestroyed = 1
                    location["DamageLevel"] = "Destroyed"
            if location["Location"] == "RightArm":
                if mech.isRightTorsoDestroyed == 1 and mech.isRightArmDestroyed == 0:
                    print("Right Arm destroyed due to Right Torso being destroyed")
                    mech.isRightArmDestroyed = 1
                    location["DamageLevel"] = "Destroyed"

        # Center Torso and Head third
        for location in mech.mech_data["Locations"]:
            if location["Location"] == 'CenterTorso' and location["DamageLevel"] == "Functional" \
                    and location["CurrentArmor"] + damage_to_center_torso <= 0:
                location["CurrentInternalStructure"] += location["CurrentArmor"] + damage_to_center_torso
                location["CurrentArmor"] = 0
                if location["CurrentInternalStructure"] <= 0:
                    location["DamageLevel"] = "Destroyed"
                    mech.isCenterTorsoDestroyed = 1
                    print("Center Torso Destroyed!")
            if location["Location"] == 'Head' and location["DamageLevel"] == "Functional" \
                    and location["CurrentArmor"] <= 0:
                location["CurrentInternalStructure"] += location["CurrentArmor"]
                location["CurrentArmor"] = 0
                if location["CurrentInternalStructure"] <= 0:
                    location["DamageLevel"] = "Destroyed"
                    mech.isHeadDestroyed = 1
                    print("Head Destroyed!")
        # Mark and print message about weapons being destroyed on body parts that are destroyed
        weapon_destroyed_message = "{} has been destroyed along with the {}"
        for location in mech.mech_data["Locations"]:
            for inventory in mech.mech_data["inventory"]:
                if location["Location"] == inventory["MountedLocation"]:
                    if location["DamageLevel"] != inventory["DamageLevel"]:
                        inventory["DamageLevel"] = location["DamageLevel"]
                        # If an ammo box gets destroyed, deduct the capacity from the weapons' ammo count
                        if inventory["ComponentDefType"] == "AmmunitionBox":
                            weapon_ammo_type = json_reference[inventory["ComponentDefID"]]["Description"]["Model"]
                            # print(weapon_ammo_type)
                            for inventory2 in mech.mech_data["inventory"]:
                                if inventory2["DamageLevel"] == "Functional" and inventory2[
                                    "ComponentDefType"] == "Weapon":
                                    weapon_ammo_type2 = json_reference[inventory2["ComponentDefID"]]["AmmoCategory"]
                                    if weapon_ammo_type != 'NotSet' and weapon_ammo_type == weapon_ammo_type2:
                                        inventory2["RemainingAmmo"] -= \
                                            json_reference["Ammo_AmmunitionBox_Generic_" + weapon_ammo_type]["Capacity"]
                        print(weapon_destroyed_message.format(
                            json_reference[inventory["ComponentDefID"]]["Description"]["UIName"],
                            inventory["MountedLocation"]))

    def determine_target_body_part(self, mech):
        i = 0
        body_part = ""
        while i == 0:
            choice = random.choice(mech.mech_data["Locations"])
            if choice["DamageLevel"] == "Functional" and choice["Location"] != "Head":
                i = 1
                body_part = choice["Location"]
        return body_part

    def after_battle(self):
        # Write/append the contents of the attack history to a csv
        with open('BattleHistory.csv', 'a') as out_file:
            # # Create field headers with new file
            # header_list = []
            # headers = vars(self.attack_history[0])
            # for item in headers:
            #     header_list.append(item)
            # header_string = ','.join(header_list)
            # out_file.write(header_string)
            # out_file.write("\n")
            # print(header_string)

            # Create records from attack history
            for attack in self.attack_history:
                record_list = []
                temp = vars(attack)
                for item in temp:
                    record_list.append(str(temp[item]))
                    record_string = ','.join(record_list)
                out_file.write(record_string)
                out_file.write("\n")
                print(record_string)


with open('BattleHistory.csv', 'w') as out_file_init:
    out_file_init.write(
        "weapon,ammo_type,damage,shots,hit_percent,attack_number,isHit,target_body_part,target_damage_taken,round,turn,attacking_mechdef_id,defending_mechdef_id,battle_id,battle_date")
    out_file_init.write("\n")
json_reference: Dict[str, Any] = load_all_json_files()
mech_list = []
mech_list2 = []
for mechdef in json_reference.keys():
    if mechdef.startswith("mechdef_"):
        mech_list.append(mechdef)
mech_list2 = mech_list.copy()
# print(random.choice(mech_list))
# print(random.choice(mech_list))
# pprint.pprint(json_reference, indent=4)  # For testing pretty print
for a in mech_list:
    for b in mech_list2:
        for _ in range(0, 1):
            mech1 = Mech("Bob", a)  # random.choice(mech_list))
            mech2 = Mech("Fred", b)  # random.choice(mech_list))
            battle1 = Battle(mech1, mech2, json_reference.copy())
            battle1.start_battle()
