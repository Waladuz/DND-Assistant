from DataManagers import cm_shared, em_shared


class BattleManager:
    def __init__(self):
        # 0 - Map Setup | 1 - Chara Placement | 2 - Roll Initiative | 3 - Battle Mode | 4 - Battle Complete
        self.current_battle_state = 0

        self.player_list = []
        self.enemy_list = []

        self.initiative_order = []

        self.current_selected_entity = None

    def start_battle(self, enemy_list):
        self.current_battle_state = 1
        self.initiative_order = []
        self.enemy_list = enemy_list

        self.player_list = []
        chara_dictionary = cm_shared.Character_From_ID_Dictionary

        i = 0

        for chara_id, chara in chara_dictionary.items():
            self.player_list.append(chara)

        for enemy in enemy_list:
            enemy.Temp_HP = enemy.Temp_HP_Max

        self.current_selected_entity = self.player_list[0]

    def set_initiative(self, initiative_list):
        entities = self.player_list + self.enemy_list

        self.initiative_order = [
            (initiative, entity)
            for initiative, entity in zip(initiative_list, entities)
        ]

        self.initiative_order.sort(
            key=lambda x: x[0],
            reverse=True
        )


        self.current_battle_state = 3

    def check_if_enemies_dead(self):
        for enemy in self.enemy_list:
            if enemy.Temp_HP > 0:
                return False
        return True
