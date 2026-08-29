import mne
import numpy as np
import scipy.signal as signal
import pandas as pd
import os
import warnings
import matplotlib.pyplot as plt

# 1. 彻底关闭底层 MNE 的全局警告
mne.set_log_level('ERROR')

def calculate_spectral_entropy(time_series, sfreq):
    # 缩短 Welch 滑动窗长，完美适应 1 秒长度的微型数据块
    frequencies, psd = signal.welch(time_series, fs=sfreq, nperseg=int(sfreq / 2)) 
    psd_norm = psd / np.sum(psd)
    return -np.sum(psd_norm * np.log2(psd_norm + 1e-12))

base_dir = "C:/mywork/eeg/dataset"
derivatives_dir = os.path.join(base_dir, "derivatives", "eeglab")
participants_file = os.path.join(base_dir, "participants.tsv")

part_df = pd.read_csv(participants_file, sep='\t')
part_df.columns = part_df.columns.str.strip()

# 聚焦因果离存冲击最强的 5Hz 离散脉冲刺激
target_freq = '5Hz'
time_points_results = []

print(f"🚀 启动 5 秒时间轴细粒度解耦切片（1秒/步）动态演化计算...")

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    
    for index, row in part_df.iterrows():
        sub_id = str(row['participant_id']).strip()
        group_label = str(row['Group']).strip() 
        gender = 'F' if 'F' in str(row['Gender']).upper() else ('M' if 'M' in str(row['Gender']).upper() else 'Unknown')
        
        eeg_file = os.path.join(derivatives_dir, sub_id, 'eeg', f"{sub_id}_task-photomark_eeg.set")
        event_file = os.path.join(base_dir, sub_id, 'eeg', f"{sub_id}_task-photomark_events.tsv")
        
        if not (os.path.exists(eeg_file) and os.path.exists(event_file)):
            continue
            
        try:
            raw = mne.io.read_raw_eeglab(eeg_file, preload=True, verbose='ERROR')
            events_df = pd.read_csv(event_file, sep='\t')
            sfreq = raw.info['freq'] if 'freq' in raw.info else raw.info['sfreq']
            
            target_ch = [ch for ch in raw.ch_names if ch.startswith('O') or ch.startswith('P')]
            raw.pick(target_ch, verbose='ERROR')
            data = raw.get_data()
            
            photo_events = events_df[events_df['value'].str.contains(target_freq, na=False)]
            if photo_events.empty: 
                continue 
                
            # 🛠️【核心修复点】：用 .iat[0] 规避一切由于 Pandas 版本迭代引发的 Indexer 混淆
            onset = float(photo_events['onset'].iat[0])
            
            # 🛡 *形状降维处理*：提取总时间轴长度（整数）
            total_time_points = data.shape[1]
            
            # 🛡️ 严格越界防御（5秒内绝不能有任何 boundary 裁剪断裂）
            if int((onset + 5) * sfreq) > total_time_points or int((onset - 5) * sfreq) < 0:
                continue
            
            # ⏳ 【时间解耦切片核心】：将 5 秒拆解为 5 个 1 秒的独立网格
            for second in range(5):
                # 刺激态的当前 1 秒
                t_stim_start = int((onset + second) * sfreq)
                t_stim_end = int((onset + second + 1) * sfreq)
                seg_stim = data[:, t_stim_start:t_stim_end]
                
                # 静息态的对应 1 秒
                t_rest_start = int((onset - 5 + second) * sfreq)
                t_rest_end = int((onset - 5 + second + 1) * sfreq)
                seg_rest = data[:, t_rest_start:t_rest_end]
                
                # 计算这 1 秒内的谱熵
                ent_rest = np.mean([calculate_spectral_entropy(seg_rest[i], sfreq) for i in range(seg_rest.shape[0])])
                ent_stim = np.mean([calculate_spectral_entropy(seg_stim[i], sfreq) for i in range(seg_stim.shape[0])])
                ent_diff = ent_stim - ent_rest
                
                time_points_results.append({
                    'sub_id': sub_id, 'Group': group_label, 'Gender': gender,
                    'Second': second + 1, 'Diff_SRE': ent_diff
                })
                
            print(f"✅ {sub_id} 5秒动态时间链（第1-5秒）谱熵切片提取成功")
            
        except Exception as e:
            print(f"❌ {sub_id} 遭遇时序切片异常: {e}")

# 转换为 DataFrame
time_df = pd.DataFrame(time_points_results)

if not time_df.empty:
    # 汇总：按疾病组别和秒数，计算每一秒的均值
    trajectory = time_df.groupby(['Group', 'Second'])['Diff_SRE'].mean().reset_index()
    print("\n📊 === 5秒内全脑网络滤波器实时演化曲线矩阵 ===")
    print(trajectory.to_string(index=False))
    
    # 🎨 绘制时间序列位移轨迹图
    plt.figure(figsize=(9, 5))
    color_map = {'A': 'crimson', 'C': 'royalblue', 'F': 'forestgreen'}
    label_map = {'A': "Alzheimer's (AD)", 'C': "Healthy Control (CN)", 'F': "Frontotemporal (FTD)"}
    
    for g in time_df['Group'].unique():
        if g in color_map:
            g_data = trajectory[trajectory['Group'] == g]
            plt.plot(g_data['Second'], g_data['Diff_SRE'], marker='o', linewidth=2.5, 
                     color=color_map[g], label=label_map[g])
        
    plt.title("Real-time Trajectory of Information Compressor over 5 Seconds (5Hz Stim)", fontsize=11)
    plt.xlabel("Time Elapsed (Seconds)", fontsize=10)
    plt.ylabel("Instantanous Entropy Change (Stim - Rest)", fontsize=10)
    plt.axhline(0, color='gray', linestyle='--', linewidth=0.8)
    plt.grid(True, linestyle=':')
    plt.legend()
    
    output_img = "C:/mywork/eeg/time_trajectory_result.png"
    plt.savefig(output_img, bbox_inches='tight')
    print(f"\n📈 5秒动态演化轨迹图已成功保存至: {output_img}！")
else:
    print("未能提取到有效数据。")
