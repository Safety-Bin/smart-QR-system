import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="스마트 QR 설비/소화기 점검 시스템", layout="wide")

# ==========================================
# 0. 세션 상태(DB 대용) 초기화: 점검 데이터 저장소
# ==========================================
if 'inspection_logs' not in st.session_state:
    st.session_state['inspection_logs'] = [
        {"시간": "2026-08-26 08:30", "공정": "1공장 FAB 주출입구", "설비번호": "EXT-01 (소화기 #1)", "외관상태": "양호", "압력상태": "정상 (녹색)", "특이사항": "이상 없음"},
        {"시간": "2026-08-26 09:15", "공정": "2공장 유틸리티룸", "설비번호": "EXT-05 (소화기 #5)", "외관상태": "양호", "압력상태": "이상 (지침 좌측 이탈)", "특이사항": "충전압 이상 발생! 교체 필요"}
    ]

st.title("📱 스마트 QR 기반 설비 및 소화기 일일 점검 시스템")
st.markdown("현장 근로자가 QR코드로 간편하게 점검하고, 관리자는 실시간으로 이상 징후를 모니터링합니다.")

# 화면 탭 분리
tab1, tab2 = st.tabs(["📲 [근로자용] QR 모바일 점검 입력", "🖥️ [관리자용] 실시간 점검 현황 및 이상 감지"])

# ==========================================
# 탭 1: 근로자용 점검 입력 화면 (모바일 화면 시뮬레이션)
# ==========================================
with tab1:
    st.subheader("📲 현장 QR 점검 인터페이스 (모바일 뷰)")
    st.info("💡 현장의 소화기/설비에 부착된 QR코드를 스캔했다고 가정하고 점검 결과를 입력합니다.")
    
    with st.form("qr_check_form"):
        col1, col2 = st.columns(2)
        with col1:
            # QR 스캔 시 자동으로 인식되는 정보 설정
            scan_process = st.selectbox("점검 공정 선택", ["1공장 FAB 주출입구", "1공장 클린룸 내부", "2공장 유틸리티룸", "물류창고 A동"])
            equipment_id = st.text_input("설비/소화기 관리번호", value="EXT-03 (소화기 #3)", help="QR 코드 인식 시 자동 입력됨")
            
        with col2:
            st.markdown("#### 🔍 소화기 자체 점검표 (소화기 부착형)")
            status_body = st.radio("1. 소화기 본체 및 호스 외관 상태", ["양호 (부식/파손 없음)", "불량 (변형, 부식, 호스 파손)"])
            status_pressure = st.selectbox("2. 압력게이지 지침 상태 (가장 중요!)", ["정상 (녹색 범위 위치)", "이상 (지침이 좌측 또는 우측 이탈 / 압력 저하)"])
            
        note = st.text_area("현장 특이사항 및 조치 필요 내용", placeholder="예: 소화기 앞 적재물 방치 또는 충전압 불량 등")
        
        submit_btn = st.form_submit_button("📤 점검 결과 실시간 전송")
        
        if submit_btn:
            # 새로운 점검 데이터 생성
            now_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            pressure_result = "정상 (녹색)" if "정상" in status_pressure else "이상 (지침 이탈)"
            
            new_log = {
                "시간": now_time,
                "공정": scan_process,
                "설비번호": equipment_id,
                "외관상태": "양호" if "양호" in status_body else "불량",
                "압력상태": pressure_result,
                "특이사항": note if note else ("이상 없음" if pressure_result.startswith("정상") else "충전압 이상 발생!")
            }
            
            # 세션 데이터베이스에 추가
            st.session_state['inspection_logs'].insert(0, new_log)
            
            if pressure_result.startswith("이상"):
                st.error(f"🚨 [긴급 경고] {equipment_id}에서 충전압 이상이 감지되어 관리자에게 즉시 전송되었습니다!")
            else:
                st.success(f"✅ {equipment_id} 점검 결과가 성공적으로 전송되었습니다. 안전한 하루 되세요!")

# ==========================================
# 탭 2: 관리자용 실시간 모니터링 대시보드
# ==========================================
with tab2:
    st.subheader("🖥️ 본사 EHS 실시간 모니터링 및 이상 감지 대시보드")
    
    logs = st.session_state['inspection_logs']
    df_logs = pd.DataFrame(logs)
    
    # 상단 요약 지표 (KPI)
    total_count = len(df_logs)
    abnormal_rows = df_logs[df_logs['압력상태'].str.contains("이상") | df_logs['외관상태'].str.contains("불량")]
    abnormal_count = len(abnormal_rows)
    
    col_kpi1, col_kpi2 = st.columns(2)
    col_kpi1.metric("오늘 누적 점검 건수", f"{total_count} 건")
    col_kpi2.metric("⚠️ 즉시 조치 필요(이상) 건수", f"{abnormal_count} 건", delta=-abnormal_count if abnormal_count > 0 else 0, delta_color="inverse")
    
    st.markdown("---")
    
    # 이상 항목이 있으면 최상단에 경고 카드 띄우기
    if abnormal_count > 0:
        st.error(f"🚨 **[긴급 알림] 현재 총 {abnormal_count}개의 설비/소화기에서 '충전압 이상' 또는 '외관 불량'이 접수되었습니다! 즉시 현장 정비팀을 파견하세요.**")
        st.dataframe(abnormal_rows, use_container_width=True)
        st.markdown("---")
        
    st.markdown("### 📋 전체 실시간 점검 로그 아카이브")
    st.dataframe(df_logs, use_container_width=True)
    
    # 엑셀 다운로드 버튼
    def to_excel(df):
        output = io.BytesIO() if 'io' in globals() else None
        # 안전한 바이트 변환
        import io as python_io
        output = python_io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Inspection_Logs')
        return output.getvalue()
        
    st.download_button(
        label="📥 실시간 점검 데이터 엑셀(Excel) 백업 다운로드",
        data=to_excel(df_logs),
        file_name='Smart_Inspection_Logs.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    