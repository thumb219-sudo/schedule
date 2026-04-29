import streamlit as st
import pandas as pd

# ------------------------------------------------------------
# 수술실 간호사 근무표 기본 앱
# ------------------------------------------------------------
# 이 앱은 Streamlit으로 만든 간단한 웹 앱입니다.
# 아직 완벽한 자동 배정 프로그램은 아니지만,
# 간호사 정보를 입력하고, 근무표를 자동으로 기본 생성한 뒤,
# 표 형태로 확인할 수 있도록 구성했습니다.
#
# 실행 방법:
# 1. 터미널에서 pip install -r requirements.txt 실행
# 2. streamlit run app.py 실행
# ------------------------------------------------------------

st.set_page_config(
    page_title="수술실 간호사 근무표 앱",
    page_icon="🏥",
    layout="wide",
)

# ------------------------------------------------------------
# 기본 조건
# ------------------------------------------------------------
TOTAL_NURSES = 32

DAY_COUNT = 21
ADMIN_COUNT = 3
EVENING_COUNT = 7
OFF_COUNT = 1

SHIFT_TYPES = ["Day", "Admin", "Evening", "Off"]
PARTS = ["NS", "OS", "GS", "URO"]


# ------------------------------------------------------------
# 앱 데이터 초기화
# ------------------------------------------------------------
def init_session_state():
    """
    Streamlit은 화면이 새로고침될 때마다 코드가 다시 실행됩니다.
    그래서 입력한 정보를 유지하기 위해 session_state를 사용합니다.
    """

    if "nurse_df" not in st.session_state:
        nurse_list = []

        for i in range(1, TOTAL_NURSES + 1):
            nurse_list.append(
                {
                    "번호": i,
                    "이름": f"간호사{i}",
                    "가능파트": PARTS[(i - 1) % len(PARTS)],
                    "메모": "",
                }
            )

        st.session_state.nurse_df = pd.DataFrame(nurse_list)

    if "schedule_df" not in st.session_state:
        st.session_state.schedule_df = pd.DataFrame()


# ------------------------------------------------------------
# 기본 근무표 생성 함수
# ------------------------------------------------------------
def create_basic_schedule(nurse_df):
    """
    간호사 정보를 기준으로 기본 근무표를 생성합니다.

    현재 배정 기준:
    - Day 21명
    - Admin 3명
    - Evening 7명
    - Off 1명

    현재는 간단한 순서 배정 방식입니다.
    추후에는 Evening 주간 순환, 휴가 신청, 파트별 숙련도 조건 등을
    추가할 수 있습니다.
    """

    schedule_rows = []

    for index, row in nurse_df.reset_index(drop=True).iterrows():
        if index < DAY_COUNT:
            shift = "Day"
        elif index < DAY_COUNT + ADMIN_COUNT:
            shift = "Admin"
        elif index < DAY_COUNT + ADMIN_COUNT + EVENING_COUNT:
            shift = "Evening"
        else:
            shift = "Off"

        schedule_rows.append(
            {
                "번호": row["번호"],
                "이름": row["이름"],
                "근무": shift,
                "파트": row["가능파트"],
                "메모": row["메모"],
            }
        )

    return pd.DataFrame(schedule_rows)


# ------------------------------------------------------------
# 앱 시작
# ------------------------------------------------------------
init_session_state()

st.title("🏥 수술실 간호사 근무표 앱")
st.caption("Day 21명 / Admin 3명 / Evening 7명 / Off 1명 기준")

# ------------------------------------------------------------
# 사이드바 메뉴
# ------------------------------------------------------------
menu = st.sidebar.radio(
    "메뉴 선택",
    [
        "홈",
        "간호사 정보 입력",
        "파트별 가능 업무 관리",
        "근무표 자동 생성",
        "근무표 확인",
    ],
)


# ------------------------------------------------------------
# 홈
# ------------------------------------------------------------
if menu == "홈":
    st.header("홈")

    st.write("수술실 간호사 32명의 근무표를 관리하기 위한 기본 앱입니다.")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("전체 간호사", f"{TOTAL_NURSES}명")
    col2.metric("Day", f"{DAY_COUNT}명")
    col3.metric("Admin", f"{ADMIN_COUNT}명")
    col4.metric("Evening / Off", f"{EVENING_COUNT}명 / {OFF_COUNT}명")

    st.subheader("수술 파트")
    st.write("NS, OS, GS, URO")

    st.info(
        "왼쪽 사이드바에서 간호사 정보를 입력하고, "
        "근무표 자동 생성 메뉴에서 기본 근무표를 만들 수 있습니다."
    )


# ------------------------------------------------------------
# 간호사 정보 입력
# ------------------------------------------------------------
elif menu == "간호사 정보 입력":
    st.header("간호사 정보 입력")

    st.write("간호사 이름, 가능 파트, 메모를 수정할 수 있습니다.")

    edited_df = st.data_editor(
        st.session_state.nurse_df,
        num_rows="fixed",
        use_container_width=True,
        column_config={
            "가능파트": st.column_config.SelectboxColumn(
                "가능파트",
                options=PARTS,
                required=True,
                help="간호사가 가능한 주요 수술 파트를 선택하세요.",
            )
        },
    )

    if st.button("간호사 정보 저장"):
        st.session_state.nurse_df = edited_df
        st.success("간호사 정보가 저장되었습니다.")


# ------------------------------------------------------------
# 파트별 가능 업무 관리
# ------------------------------------------------------------
elif menu == "파트별 가능 업무 관리":
    st.header("파트별 가능 업무 관리")

    st.write("NS, OS, GS, URO 파트별 가능 인원을 확인합니다.")

    part_count = (
        st.session_state.nurse_df["가능파트"]
        .value_counts()
        .reindex(PARTS, fill_value=0)
        .reset_index()
    )

    part_count.columns = ["파트", "가능 인원"]

    st.subheader("파트별 가능 인원")
    st.dataframe(part_count, use_container_width=True)

    st.subheader("파트별 간호사 목록")

    selected_part = st.selectbox("확인할 파트 선택", PARTS)

    filtered_df = st.session_state.nurse_df[
        st.session_state.nurse_df["가능파트"] == selected_part
    ]

    st.dataframe(filtered_df, use_container_width=True)


# ------------------------------------------------------------
# 근무표 자동 생성
# ------------------------------------------------------------
elif menu == "근무표 자동 생성":
    st.header("근무표 자동 생성")

    st.write("현재 입력된 간호사 정보를 바탕으로 기본 근무표를 생성합니다.")

    st.warning(
        "현재 자동 생성은 기본 순서 배정입니다. "
        "추후 Evening 주간 순환, 휴가 신청, 파트별 숙련도 조건 등을 추가할 수 있습니다."
    )

    if st.button("기본 근무표 생성"):
        st.session_state.schedule_df = create_basic_schedule(st.session_state.nurse_df)
        st.success("기본 근무표가 생성되었습니다.")

    if not st.session_state.schedule_df.empty:
        st.subheader("생성된 근무표 미리보기")
        st.dataframe(st.session_state.schedule_df, use_container_width=True)


# ------------------------------------------------------------
# 근무표 확인
# ------------------------------------------------------------
elif menu == "근무표 확인":
    st.header("근무표 확인")

    if st.session_state.schedule_df.empty:
        st.info("아직 생성된 근무표가 없습니다. '근무표 자동 생성' 메뉴에서 먼저 생성하세요.")

    else:
        st.subheader("전체 근무표")
        st.dataframe(st.session_state.schedule_df, use_container_width=True)

        st.subheader("근무 형태별 인원 확인")

        shift_count = (
            st.session_state.schedule_df["근무"]
            .value_counts()
            .reindex(SHIFT_TYPES, fill_value=0)
            .reset_index()
        )

        shift_count.columns = ["근무 형태", "인원"]

        st.dataframe(shift_count, use_container_width=True)

        st.subheader("근무 형태별 보기")

        selected_shift = st.selectbox("근무 형태 선택", SHIFT_TYPES)

        shift_df = st.session_state.schedule_df[
            st.session_state.schedule_df["근무"] == selected_shift
        ]

        st.dataframe(shift_df, use_container_width=True)
