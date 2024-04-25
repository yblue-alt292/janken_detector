import numpy as np

# yolo出力ラベルの対応表
hands_dic = {
    0:'rock',
    1:'paper',
    2:'scissors'
}

# じゃんけんの勝敗テーブル
PvC_table = {
    'rock': {'rock': 'tie', 'scissors':'player', 'paper': 'cp'},
    'scissors': {'rock': 'cp', 'scissors':'tie', 'paper': 'player'},
    'paper': {'rock': 'player', 'scissors':'cp', 'paper': 'tie'}
}


def janken(ID_player_hands, ID_com_hand):   # PC1台vs人間複数でのじゃんけん勝者を決定
    # 出た手IDのセットを取得
    p_set = set(ID_player_hands)
    c_set = set([ID_com_hand])

    all_set = p_set.union(c_set)
    if len(all_set) == 2: # 勝負がつくとき
        ID_player_hand = list(p_set.difference(c_set))[0]   # PCと違う手を出したプレイヤーの手
        winner = judgement(ID_player_hand, ID_com_hand)
    else:   # あいこになるとき
        winner = 'tie'    
    return winner


def gen_com_hand():     # ランダムにPCの手を生成
    ID_com_hand = np.random.randint(3)
    return ID_com_hand


def judgement(ID_player_hand, ID_com_hand):     # PC1台vsプレイヤー1人のじゃんけん勝者を判定
    player_hand = hands_dic[ID_player_hand]
    com_hand = hands_dic[ID_com_hand]
    
    # 勝敗判定テーブルをもとに勝者をきめる
    current_PvC_table = PvC_table[player_hand]
    winner = current_PvC_table[com_hand]
    return winner


if __name__ == '__main__':
    players = 2

    ID_player_hands = [gen_com_hand() for _ in range(players)]
    print(f'PLAYER hands: {[hands_dic[ID_player_hand] for ID_player_hand in ID_player_hands]}')
    ID_com_hand = gen_com_hand()

    print(f'COM hand: {hands_dic[ID_com_hand]}')

    winner = janken(ID_player_hands, ID_com_hand)
    print(f'WINNER: {winner}')

