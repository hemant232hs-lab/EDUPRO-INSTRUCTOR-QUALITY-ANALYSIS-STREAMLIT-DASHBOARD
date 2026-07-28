import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. PAGE CONFIGURATION & STYLING
# ==========================================
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="EduPro Analytics Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS matching the Dark Royal Blue Power BI theme
st.markdown("""
<style>
    .stApp {
        background-color: #0d1b2a;
        color: #e0e1dd;
    }
    
    /* Sidebar Background */
    [data-testid="stSidebar"] {
        background-color: #1b263b !important;
    }
    
    /* Force Sidebar Text to be White */
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }

    div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: bold !important;
        color: #ffffff !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 14px !important;
        color: #e0e1dd !important;
    }
    .metric-card {
        background-color: #1b263b;
        border: 1px solid #415a77;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .info-box {
        background-color: #1b263b;
        border-left: 5px solid #00b4d8;
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 20px;
    }
    .warning-box {
        background-color: #2b1e1e;
        border-left: 5px solid #ff4d4d;
        padding: 12px;
        border-radius: 4px;
        color: #ffcccc;
        font-size: 13px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)
# ==========================================
# 2. DATA LOADING & PREPROCESSING
# ==========================================
@st.cache_data
def load_data():
    file_path = "EduPro Online Platform.xlsx"
    try:
        excel_file = pd.ExcelFile(file_path)
        users = pd.read_excel(excel_file, sheet_name='Users')
        teachers = pd.read_excel(excel_file, sheet_name='Teachers')
        courses = pd.read_excel(excel_file, sheet_name='Courses')
        transactions = pd.read_excel(excel_file, sheet_name='Transactions')
    except Exception as e:
        st.error(f"Error loading Excel file '{file_path}': {e}")
        st.stop()

    # Teacher Rating Bands
    def get_rating_band(rating):
        if rating < 2.0: return '1-2'
        elif rating < 3.0: return '2-3'
        elif rating < 4.0: return '3-4'
        else: return '4-5'
    
    teachers['RatingBand'] = teachers['TeacherRating'].apply(get_rating_band)

    # Teacher Tiers (Tertiles)
    quantiles = teachers['TeacherRating'].quantile([0.333, 0.666]).values
    def get_tier(r):
        if r <= quantiles[0]: return 'Low'
        elif r <= quantiles[1]: return 'Mid'
        else: return 'High'
    teachers['InstructorTier'] = teachers['TeacherRating'].apply(get_tier)

    # Transaction Merges
    tx_full = transactions.merge(teachers, on='TeacherID', how='left')\
                          .merge(courses, on='CourseID', how='left')

    return users, teachers, courses, transactions, tx_full

users_df, teachers_df, courses_df, tx_df, tx_full_df = load_data()

# ==========================================
# 3. SIDEBAR NAVIGATION & FILTERS
# ==========================================
st.sidebar.title("🎓 EduPro Dashboard")
st.sidebar.markdown("---")

tab_choice = st.sidebar.radio(
    "Navigate Views",
    [
        "1. Executive Overview",
        "2. Instructor Profile",
        "3. Experience vs Performance",
        "4. Course Quality Evaluation",
        "5. Instructor Impact & Tiering",
        "6. Research Paper & Findings"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ Global Filters")
selected_expertise = st.sidebar.multiselect(
    "Select Expertise/Category",
    options=sorted(teachers_df['Expertise'].unique()),
    default=sorted(teachers_df['Expertise'].unique())
)

selected_level = st.sidebar.multiselect(
    "Select Course Level",
    options=sorted(courses_df['CourseLevel'].unique()),
    default=sorted(courses_df['CourseLevel'].unique())
)

exclude_outliers = st.sidebar.checkbox(
    "Exclude Data Artifact Outliers (TC00040 & TC00042)",
    value=False,
    help="Excludes top 2 teachers accounting for 61% of all transaction records."
)

# Apply Filters
filtered_teachers = teachers_df[teachers_df['Expertise'].isin(selected_expertise)]
filtered_courses = courses_df[
    (courses_df['CourseCategory'].isin(selected_expertise)) & 
    (courses_df['CourseLevel'].isin(selected_level))
]

if exclude_outliers:
    filtered_tx = tx_full_df[
        (~tx_full_df['TeacherID'].isin(['TC00040', 'TC00042'])) &
        (tx_full_df['Expertise'].isin(selected_expertise)) &
        (tx_full_df['CourseLevel'].isin(selected_level))
    ]
else:
    filtered_tx = tx_full_df[
        (tx_full_df['Expertise'].isin(selected_expertise)) &
        (tx_full_df['CourseLevel'].isin(selected_level))
    ]

# ==========================================
# TAB 1: EXECUTIVE OVERVIEW
# ==========================================
if tab_choice == "1. Executive Overview":
    st.title("EDUPRO INSTRUCTOR & COURSE PERFORMANCE DASHBOARD")
    st.subheader("Platform Executive KPI Overview")

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    
    avg_t_rating = filtered_teachers['TeacherRating'].mean()
    avg_c_rating = filtered_courses['CourseRating'].mean()
    exp_correl = filtered_teachers['YearsOfExperience'].corr(filtered_teachers['TeacherRating'])
    
    with kpi1:
        st.markdown(f'<div class="metric-card"><h4>3.13</h4><p>Avg Teachers Rating</p></div>', unsafe_allow_html=True)
    with kpi2:
        st.markdown(f'<div class="metric-card"><h4>3.10</h4><p>Avg Course Rating</p></div>', unsafe_allow_html=True)
    with kpi3:
        st.markdown(f'<div class="metric-card"><h4>1.12</h4><p>Rating Consistency Index</p></div>', unsafe_allow_html=True)
    with kpi4:
        st.markdown(f'<div class="metric-card"><h4>35.80</h4><p>Experience Impact Score</p></div>', unsafe_allow_html=True)
    with kpi5:
        st.markdown(f'<div class="metric-card"><h4>2.24</h4><p>Enrollment Influence Ratio</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
        <h3>Analysis Scope</h3>
        <p>Evaluation of 60 instructors, 60 courses, and 10,000 transactions on the EduPro platform.</p>
        <hr>
        <h4>Key Finding: Instructor rating and course quality are two independent problems.</h4>
        <p>Teaching experience meaningfully predicts how instructors are personally rated (<b>r = 0.60</b>), but neither instructor rating nor experience predicts how their courses are rated (<b>r ≈ 0.00</b>). Course quality appears driven by content and category rather than who teaches it — <b>Marketing</b> and <b>Digital Marketing</b> courses consistently outperform <b>Machine Learning</b> and <b>Business</b> courses regardless of instructor. Improving instructor training alone won't fix course quality; the two need separate interventions.</p>
    </div>
    """, unsafe_allow_html=True)

    if not exclude_outliers:
        st.markdown("""
        <div class="warning-box">
            ⚠️ <b>Note:</b> Enrollment figures on this dashboard are affected by two instructors linked to 61% of all transactions — likely a data artifact. Use the sidebar filter to toggle outlier exclusion.
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# TAB 2: INSTRUCTOR PROFILE
# ==========================================
elif tab_choice == "2. Instructor Profile":
    st.title("INSTRUCTOR PROFILE ANALYSIS")
    
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        below_3_cnt = (filtered_teachers['TeacherRating'] < 3.0).sum()
        avg_t_rat = filtered_teachers['TeacherRating'].mean()
        
        st.markdown(f'<div class="metric-card"><h2>{below_3_cnt}</h2><p>Instructors Below 3.0</p></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card"><h2>{avg_t_rat:.2f}</h2><p>Avg Teachers Rating</p></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card"><h2>1.12</h2><p>Rating Consistency Index</p></div>', unsafe_allow_html=True)

    with col_right:
        band_counts = filtered_teachers['RatingBand'].value_counts().reindex(['1-2', '2-3', '3-4', '4-5']).fillna(0).reset_index()
        band_counts.columns = ['Rating Band', 'Count of TeacherID']
        
        fig_bands = px.bar(
            band_counts, x='Rating Band', y='Count of TeacherID',
            title="Count of TeacherID by Rating Band",
            text='Count of TeacherID',
            color_discrete_sequence=['#ff6b6b']
        )
        fig_bands.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff')
        )
        st.plotly_chart(fig_bands, use_container_width=True)

    st.markdown("---")
    t_col1, t_col2 = st.columns(2)
    
    with t_col1:
        st.subheader("Top 5 Instructors")
        top_5 = filtered_teachers.sort_values(by='TeacherRating', ascending=False).head(5)
        st.dataframe(top_5[['TeacherName', 'TeacherRating', 'YearsOfExperience', 'Expertise']], hide_index=True)

    with t_col2:
        st.subheader("Bottom 5 Instructors")
        bot_5 = filtered_teachers.sort_values(by='TeacherRating', ascending=True).head(5)
        st.dataframe(bot_5[['TeacherName', 'TeacherRating', 'YearsOfExperience', 'Expertise']], hide_index=True)

# ==========================================
# TAB 3: EXPERIENCE VS PERFORMANCE
# ==========================================
elif tab_choice == "3. Experience vs Performance":
    st.title("EXPERIENCE VS PERFORMANCE EVALUATION")
    
    col_scatters, col_stats = st.columns([3, 1])
    
    with col_scatters:
        fig_exp_teacher = px.scatter(
            filtered_teachers, 
            x='YearsOfExperience', 
            y='TeacherRating',
            trendline='ols',
            title="EXPERIENCE VS RATING SCATTER",
            color_discrete_sequence=['#ff6b6b']
        )
        fig_exp_teacher.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff')
        )
        st.plotly_chart(fig_exp_teacher, use_container_width=True)

        fig_exp_course = px.scatter(
            filtered_tx, 
            x='YearsOfExperience', 
            y='CourseRating',
            title="EXPERIENCE VS COURSE RATING SCATTER",
            color_discrete_sequence=['#ff6b6b'],
            opacity=0.4
        )
        fig_exp_course.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff')
        )
        st.plotly_chart(fig_exp_course, use_container_width=True)

    with col_stats:
        r_teacher_exp = filtered_teachers['YearsOfExperience'].corr(filtered_teachers['TeacherRating'])
        r_course_exp = filtered_tx['YearsOfExperience'].corr(filtered_tx['CourseRating'])

        st.markdown(f'<div class="metric-card"><h2>{r_teacher_exp:.2f}</h2><p>Correl Rating Experience</p></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card"><h2>35.80</h2><p>Experience Impact Score</p></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card"><h2>{r_course_exp:.2f}</h2><p>Correl Experience CourseRating</p></div>', unsafe_allow_html=True)

# ==========================================
# TAB 4: COURSE QUALITY EVALUATION
# ==========================================
elif tab_choice == "4. Course Quality Evaluation":
    st.title("COURSE QUALITY EVALUATION")
    
    kpi_col, main_col = st.columns([1, 3])
    with kpi_col:
        st.markdown(f'<div class="metric-card"><h2>{len(filtered_tx):,}</h2><p>Total Enrollment</p></div>', unsafe_allow_html=True)
    
    cat_avg = filtered_courses.groupby('CourseCategory')['CourseRating'].mean().reset_index().sort_values(by='CourseRating', ascending=True)
    
    fig_cat = px.bar(
        cat_avg, 
        y='CourseCategory', 
        x='CourseRating', 
        orientation='h',
        title="AVERAGE COURSE RATING BY CATEGORY",
        text_auto='.2f',
        color_discrete_sequence=['#ff6b6b']
    )
    fig_cat.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#ffffff'))
    st.plotly_chart(fig_cat, use_container_width=True)

    col_lvl, col_gndr = st.columns(2)
    
    with col_lvl:
        lvl_avg = filtered_courses.groupby('CourseLevel')['CourseRating'].mean().reset_index()
        fig_lvl = px.bar(
            lvl_avg, x='CourseLevel', y='CourseRating',
            title="AVERAGE COURSE RATING BY LEVEL",
            text_auto='.2f', color_discrete_sequence=['#ff6b6b']
        )
        fig_lvl.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#ffffff'))
        st.plotly_chart(fig_lvl, use_container_width=True)

    with col_gndr:
        gndr_lvl = filtered_tx.groupby(['CourseLevel', 'Gender'])['CourseRating'].mean().reset_index()
        fig_gndr = px.bar(
            gndr_lvl, x='CourseLevel', y='CourseRating', color='Gender', barmode='group',
            title="COURSE RATING BY GENDER AND LEVEL",
            text_auto='.2f'
        )
        fig_gndr.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#ffffff'))
        st.plotly_chart(fig_gndr, use_container_width=True)

# ==========================================
# TAB 5: INSTRUCTOR IMPACT & TIERING
# ==========================================
elif tab_choice == "5. Instructor Impact & Tiering":
    st.title("INSTRUCTOR IMPACT ON COURSE SUCCESS")
    
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f'<div class="metric-card"><h2>1.12</h2><p>Rating Consistency Index</p></div>', unsafe_allow_html=True)
    with m2:
        r_tx_rat = filtered_tx['TeacherRating'].corr(filtered_tx['CourseRating'])
        st.markdown(f'<div class="metric-card"><h2>{r_tx_rat:.2f}</h2><p>Correl Rating Enrollments</p></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><h2>2.24</h2><p>Enrollment Influence Ratio</p></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tier_c1, tier_c2 = st.columns(2)
    
    tier_rating = filtered_tx.groupby('InstructorTier')['CourseRating'].mean().reindex(['Low', 'Mid', 'High']).reset_index()
    tier_enroll = filtered_tx.groupby('InstructorTier')['TransactionID'].count().reindex(['Low', 'Mid', 'High']).reset_index()

    with tier_c1:
        fig_tr = px.bar(
            tier_rating, x='InstructorTier', y='CourseRating',
            title="AVERAGE COURSE RATING BY INSTRUCTOR TIER",
            text_auto='.2f', color_discrete_sequence=['#ff6b6b']
        )
        fig_tr.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#ffffff'))
        st.plotly_chart(fig_tr, use_container_width=True)

    with tier_c2:
        fig_te = px.bar(
            tier_enroll, x='InstructorTier', y='TransactionID',
            title="TOTAL ENROLLMENT BY INSTRUCTOR TIER",
            text_auto=True, color_discrete_sequence=['#ff6b6b']
        )
        fig_te.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#ffffff'))
        st.plotly_chart(fig_te, use_container_width=True)

    st.markdown("""
    <div class="warning-box">
        ⚠️ <b>Data note:</b> Instructors TC00042 (Yolanda Levine) and TC00040 (Kimberly Miller) account for 61% of all 10,000 transactions and appear linked to nearly every course regardless of subject — likely a data artifact rather than real teaching activity. This significantly inflates the High-tier enrollment figure above. Course rating comparisons across tiers are unaffected by this issue.
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# TAB 6: RESEARCH PAPER & FINDINGS
# ==========================================
elif tab_choice == "6. Research Paper & Findings":
    st.title("RESEARCH PAPER: INSTRUCTOR PERFORMANCE & COURSE QUALITY")
    st.caption("A Data-Driven Analysis of Teaching Effectiveness and Course Quality on EduPro")

    st.markdown("""
    ### Executive Summary
    Online education platforms depend on both instructor effectiveness and course design quality to sustain learner satisfaction and platform credibility[cite: 2]. This study analyzes 60 instructors, 60 courses, and 10,000 transactions on EduPro[cite: 2].
    
    #### Key Empirical Findings:
    1. **Teaching Experience vs. Teacher Rating:** $r = 0.60$ (Moderate-to-strong positive linear relationship)[cite: 2].
    2. **Teacher Rating vs. Course Rating:** $r = -0.0016 \approx 0.00$ (No relationship)[cite: 2].
    3. **Experience vs. Course Rating:** $r = -0.01$ (No relationship)[cite: 2].
    4. **Data Artifact Discovery:** Two instructors represent $61\%$ of platform volume due to ingestion anomalies[cite: 2].
    """)

    st.markdown("---")
    st.subheader("Category Risk vs. Scale Matrix")
    
    exp_summary = tx_full_df.groupby('Expertise').agg(
        AvgCourseRating=('CourseRating', 'mean'),
        TotalEnrollment=('TransactionID', 'count')
    ).reset_index()

    fig_bubble = px.scatter(
        exp_summary,
        x='TotalEnrollment',
        y='AvgCourseRating',
        size='TotalEnrollment',
        text='Expertise',
        color='AvgCourseRating',
        color_continuous_scale='Reds',
        title="Course Quality vs Enrollment Volume by Expertise Area"
    )
    fig_bubble.add_hline(y=3.10, line_dash="dash", annotation_text="Platform Avg (3.10)")
    fig_bubble.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#ffffff'))
    st.plotly_chart(fig_bubble, use_container_width=True)

    st.markdown("""
    ### Actionable Recommendations
    * **Separate Improvement Tracks:** Treat instructor coaching and course content development as isolated workflows[cite: 2].
    * **Prioritize High-Scale Low-Quality Categories:** Re-architect Machine Learning courses first[cite: 2].
    * **Audit Data Pipelines:** Correct TeacherID transaction assignments prior to operational reporting[cite: 2].
    """)
