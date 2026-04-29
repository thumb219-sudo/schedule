
import streamlit as st
import pandas as pd
from io import StringIO

# ------------------------------------------------------------
# 수술실 간호사 근무표 앱
# ------------------------------------------------------------
# 이 앱은 수술실 간호사 32명의 정보를 입력하고,
# Day / Admin / Evening / Off 근무표를 기본 생성하는 앱입니다.
#
# 이번 버전의 특징:
# 1. 간호사 정보를 하나하나 입력하지 않고 붙여넣기 가능
# 2. PART를 NS,GS,URO,OS처럼 여러 개 입력 가능
# 3. SENIOR 가능여부 입력 가능
# 4. 행정 간호사 3명 포함
# ------------------------------------------------------------

st.set_page_config(
    page_title="수술실 근무 테이블 앱",
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
# 기본 간호사 정보
# ------------------------------------------------------------
DEFAULT_NURSE_DATA = """이름\tPART\tSENIOR 가능여부
조희정\t행정(팀장)\t
조성원\t행정(책임)\t
최종선\t행정(책임)\t
이우림\tNS,GS\t가능
한현희\tNS,GS,URO,OS\t가능
김서리\tNS,GS,URO\t가능
황민경\tNS,OS,GS,URO\t가능
김정은\tOS,URO,GS\t가능
이유경\tOS,URO\t가능
이다운\tOS,URO\t가능
한정윤\tGS,NS,URO\t가능
임정민\tNS,OS,GS,URO\t가능
이연경\tOS,NS\t가능
류혜리\tNS,OS,GS,URO\t가능
정수연\tGS,NS,URO\t
이지민\tNS,OS,GS,URO\t가능
김유정\tOS,NS,URO,GS\t
유혜원\tNS,GS\t
김미정\tNS,GS,OS,URO\t
한혜진\tNS,OS,GS,URO\t
진솔\tOS,NS,GS\t
김동호\tOS,URO,GS\t
김정연\tNS,GS,URO\t
이태림\tOS,NS,GS,URO\t
김길영\tOS\t
황랑경\tNS,GS,URO\t
강은혜\tOS,GS,URO\t
류원영\tNS\t
변수민\tOS\t
서은정\tNS\t
김광진\tOS\t
금민애\tOS\t
"""


# ------------------------------------------------------------
# 붙여넣은 간호사 정보를 표로 바꾸는 함수
# ------------------------------------------------------------
def parse_nurse_text(text):
    """
    엑셀이나 구글 스프레드시트에서 복사한 내용을
    앱에서 사용할 수 있는 표 형태로 바꾸는 함수입니다.

    예상 형식:
    이름    PART    SENIOR 가능여부
    조희정  행정(팀장)
    이우림  NS,GS   가능
    """

    text = text.strip()

    if not text:
        return pd.DataFrame(columns=["번호", "이름", "PART", "SENIOR 가능여부", "메모"])

    # 탭으로 구분된 표를 읽습니다.
    # 구글 스프레드시트나 엑셀에서 복사하면 보통 탭으로 들어옵니다.
    df = pd.read_csv(StringIO(text), sep="\t", header=None)

    # 첫 줄이 제목이면 제거합니다.
    first_row = " ".join(df.iloc[0].astype(str).tolist())
    if "이름" in first_row or "PART" in first_row:
        df = df.iloc[1:].reset_index(drop=True)

    rows = []

    for i, row in df.iterrows():
        values = [str(v).strip() for v in row.tolist()]

        name = values[0] if len(values) > 0 and values[0] != "nan" else ""
        part = values[1] if len(values) > 1 and values[1] != "nan" else ""
        senior = values[2] if len(values) > 2 and values[2] != "nan" else ""

        if name == "":
            continue

        rows.append(
            {
                "번호": len(rows) + 1,
                "이름": name,
                "PART": part,
                "SENIOR 가능여부": senior,
                "메모": "",
            }
        )

    return pd.DataFrame(rows)


# ------------------------------------------------------------
# 기본 근무표 생성 함수
# ------------------------------------------------------------
def create_basic_schedule(nurse_df):
    """
    기본 근무표를 생성합니다.

    현재 기준:
    - 행정 표시가 있는 사람은 Admin 우선 배정
    - 나머지 중 앞에서부터 Day 21명
    - 그다음 Evening 7명
    - 마지막 Off 1명

    추후에는 이브닝 주간 순환, 휴가자 지정, 파트별 인원 조건을 추가할 수 있습니다.
    """

    df = nurse_df.copy().reset_index(drop=True)

    schedule_rows = []

    # 행정 간호사 먼저 분리
    admin_df = df[df["PART"].str.contains("행정", na=False)].copy()
    work_df = df[~df["PART"].str.contains("행정", na=False)].copy()

    # 행정 간호사 배정
    for _, row in admin_df.iterrows():
        schedule_rows.append(
            {
                "번호": row["번호"],
                "이름": row["이름"],
                "근무": "Admin",
                "PART": row["PART"],
                "SENIOR 가능여부": row["SENIOR 가능여부"],
                "메모": row["메모"],
            }
        )

    # 일반 간호사 배정
    for index, row in work_df.reset_index(drop=True).iterrows():
        if index < DAY_COUNT:
            shift = "Day"
        elif index < DAY_COUNT + EVENING_COUNT:
            shift = "Evening"
        else:
            shift = "Off"

        schedule_rows.append(
            {
                "번호": row["번호"],
                "이름": row["이름"],
                "근무": shift,
                "PART": row["PART"],
                "SENIOR 가능여부": row["SENIOR 가능여부"],
                "메모": row["메모"],
            }
        )

    schedule_df = pd.DataFrame(schedule_rows)

    return schedule_df


# ------------------------------------------------------------
# 앱 데이터 초기화
# ------------------------------------------------------------
def init_session_state():
    if "nurse_df" not in st.session_state:
        st.session_state.nurse_df = parse_nurse_text(DEFAULT_NURSE_DATA)

    if "schedule_df" not in st.session_state:
        st.session_state.schedule_df = pd.DataFrame()


init_session_state()


# ------------------------------------------------------------
# 앱 제목
# ------------------------------------------------------------
st.title("🏥 수술실 근무 테이블 앱")
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
        "작업테이블 자동 생성",
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

    col1.metric("전체 간호사", f"{len(st.session_state.nurse_df)}명")
    col2.metric("Day", f"{DAY_COUNT}명")
    col3.metric("Admin", f"{ADMIN_COUNT}명")
    col4.metric("Evening / Off", f"{EVENING_COUNT}명 / {OFF_COUNT}명")

    st.subheader("수술 파트")
    st.write("NS, OS, GS, URO")

    st.info("왼쪽 메뉴에서 간호사 정보를 확인하고, 작업테이블 자동 생성 메뉴에서 근무표를 만들 수 있습니다.")


# ------------------------------------------------------------
# 간호사 정보 입력
# ------------------------------------------------------------
elif menu == "간호사 정보 입력":
    st.header("간호사 정보 입력")

    tab1, tab2 = st.tabs(["현재 정보 확인/수정", "복사해서 한 번에 붙여넣기"])

    with tab1:
        st.write("현재 저장된 간호사 정보입니다. 필요한 부분은 직접 수정할 수 있습니다.")

        edited_df = st.data_editor(
            st.session_state.nurse_df,
            num_rows="dynamic",
            use_container_width=True,
        )

        if st.button("수정한 간호사 정보 저장"):
            st.session_state.nurse_df = edited_df
            st.session_state.schedule_df = pd.DataFrame()
            st.success("간호사 정보가 저장되었습니다.")

    with tab2:
        st.write("엑셀이나 구글 스프레드시트에서 표를 복사해서 아래 칸에 붙여넣으세요.")

        pasted_text = st.text_area(
            "간호사 정보 붙여넣기",
            value=DEFAULT_NURSE_DATA,
            height=400,
        )

        if st.button("붙여넣은 내용으로 저장"):
            new_df = parse_nurse_text(pasted_text)
            st.session_state.nurse_df = new_df
            st.session_state.schedule_df = pd.DataFrame()

            st.success(f"{len(new_df)}명의 간호사 정보가 저장되었습니다.")
            st.dataframe(new_df, use_container_width=True)


# ------------------------------------------------------------
# 파트별 가능 업무 관리
# ------------------------------------------------------------
elif menu == "파트별 가능 업무 관리":
    st.header("파트별 가능 업무 관리")

    st.write("한 명이 여러 파트를 할 수 있기 때문에, PART에 포함된 값을 기준으로 계산합니다.")

    part_summary = []

    for part in PARTS:
        count = st.session_state.nurse_df["PART"].str.contains(part, na=False).sum()
        part_summary.append({"파트": part, "가능 인원": count})

    part_df = pd.DataFrame(part_summary)

    st.subheader("파트별 가능 인원")
    st.dataframe(part_df, use_container_width=True)

    st.subheader("파트별 간호사 목록")

    selected_part = st.selectbox("확인할 파트 선택", PARTS)

    filtered_df = st.session_state.nurse_df[
        st.session_state.nurse_df["PART"].str.contains(selected_part, na=False)
    ]

    st.dataframe(filtered_df, use_container_width=True)


# ------------------------------------------------------------
# 작업테이블 자동 생성
# ------------------------------------------------------------
elif menu == "작업테이블 자동 생성":
    st.header("작업테이블 자동 생성")

    st.write("현재 입력된 간호사 정보를 바탕으로 기본 근무표를 생성합니다.")

    st.warning(
        "현재 자동 생성은 기본 순서 배정입니다. "
        "추후 Evening 주간 순환, 휴가 신청, 파트별 필요 인원 조건을 추가할 수 있습니다."
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
        st.info("'작업테이블 자동 생성' 메뉴에서 먼저 기본 근무표를 생성하세요.")

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
