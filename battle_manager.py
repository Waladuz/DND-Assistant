from DataManagers import cm_shared, em_shared


class BattleManager:
    def __init__(self):
        # 0 - Map Setup | 1 - Chara Placement | 2 - Roll Initiative | 3 - Battle Mode | 4 - Battle Complete
        self.current_battle_state = 0

        self.player_list = []
        self.enemy_list = []

        self.initiative_to_entity_dictionary = {}

        self.current_selected_entity = None

    def start_battle(self, enemy_list):
        self.current_battle_state = 1
        self.player_list = []
        self.enemy_list = enemy_list
        chara_dictionary = cm_shared.Character_From_ID_Dictionary

        i = 0

        for chara_id, chara in chara_dictionary.items():
            self.player_list.append(chara)

        for enemy in enemy_list:
            enemy.Temp_HP = enemy.Temp_HP_Max

        self.current_selected_entity = self.player_list[0]

    def set_initiative(self, initiative_list):

        for i, initiative in enumerate(initiative_list):
            self.initiative_to_entity_dictionary[initiative] = (self.player_list + self.enemy_list)[i]

        self.initiative_to_entity_dictionary = dict(sorted(self.initiative_to_entity_dictionary.items(), reverse=True))

        self.current_battle_state = 3
