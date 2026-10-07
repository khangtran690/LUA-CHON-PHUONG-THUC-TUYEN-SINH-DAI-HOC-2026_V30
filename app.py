import os
import json
import smtplib
import re
import time
import requests
import io
import math
import html
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
from fpdf import FPDF

# ---------------------------------------------------------
# CẤU HÌNH GIAO DIỆN & TỪ ĐIỂN ĐA NGÔN NGỮ (VI/EN)
# ---------------------------------------------------------
st.set_page_config(
    page_title="ADMISSION ELIGIBILITY CHECKER 2026",
    layout="wide"
)

TRANS = {
    "vi": {
        "page_title": "🎓 PHƯƠNG THỨC XÉT TUYỂN ĐẠI HỌC 2026 PHÙ HỢP",
        "page_subtitle": "Hệ thống tra cứu & tính điểm đầy đủ tất cả phương thức cho 4 trường: UEH - BK TPHCM - FTU - BKHN",
        "login_header": "🔐 ĐĂNG NHẬP HỆ THỐNG",
        "login_user": "Tên đăng nhập",
        "login_pass": "Mật khẩu",
        "login_btn": "Đăng nhập",
        "login_checking": "Đang kiểm tra thông tin đăng nhập...",
        "login_err_inactive": "Tài khoản của bạn đã bị TẠM NGƯỜI HOẠT ĐỘNG!",
        "login_err_pass": "Mật khẩu không chính xác!",
        "login_err_notfound": "Tài khoản không tồn tại hoặc không thể kết nối dữ liệu!",
        "login_welcome": "Đăng nhập thành công! Xin chào ",
        "login_warning": "⚠️ **HỆ THỐNG TRA CỨU & TÍNH ĐIỂM XÉT TUYỂN CÁC TRƯỜNG UEH - BK TPHCM - FTU - BKHN**\n\n*Bạn cần đăng nhập để sử dụng dịch vụ*",
        "logout_btn": "Đăng xuất",
        "expired_title": "⏰ Tài khoản đã HẾT HẠN vào:\n",
        "valid_until": "⏳ Hạn dùng đến:\n",
        "btn_export": "📄 XUẤT KẾT QUẢ",
        "btn_admin_mgmt": "⚙️ Quản lý người dùng",
        "sec_applicant": "📋 THÔNG TIN ỨNG VIÊN",
        "fullname": "Họ và tên",
        "cccd": "Số CCCD",
        "sec_exam": "1. Kỳ Thi ĐGNL / Chứng Chỉ",
        "sec_achieve": "2. Thành Tích Học Tập & Giải Thưởng",
        "sec_gpa": "3. Điểm Học Bạ THPT (GPA 3 Năm)",
        "sec_thpt": "4. Điểm Thi Tốt Nghiệp THPT 2026",
        "sat_label": "Điểm SAT (0 - 1600)",
        "ielts_label": "Điểm IELTS Academic (0 - 9.0)",
        "vact_label": "Điểm V-ACT (ĐGNL ĐHQG TP.HCM: 0 - 1200)",
        "hsa_label": "Điểm HSA (ĐGNL ĐHQG Hà Nội: 0 - 150)",
        "tsa_label": "Điểm TSA (ĐGTD BK Hà Nội: 0 - 100)",
        "chuyen_label": "Học sinh THPT Chuyên / Năng khiếu (3 năm)",
        "hsg_tinh_label": "Giải HSG Cấp Tỉnh/Thành phố",
        "hsg_quocgia_label": "Giải HSG Cấp Quốc Gia",
        "gpa_math": "GPA Môn Toán",
        "gpa_eng": "GPA Môn Tiếng Anh",
        "gpa_sub3": "GPA Môn thứ 3 (Lý/Hóa/Văn/...)",
        "gpa_avg": "GPA Trung Bình Tất Cả Các Môn THPT",
        "thpt_math": "Điểm Thi THPT Môn Toán",
        "thpt_eng": "Điểm Thi THPT Môn Tiếng Anh",
        "thpt_sub3": "Điểm Thi THPT Môn thứ 3 (Lý/Hóa/Văn/...)",
        "priority_score": "Điểm Ưu Tiên KV / ĐTD (Thang 30)",
        "opt_best": "KẾT QUẢ TỐI ƯU NHẤT",
        "opt_score": "Điểm Xét Tuyển Tối Ưu",
        "score_with_ielts_bonus": "Có tính Điểm cộng IELTS",
        "score_without_ielts_bonus": "Không tính Điểm cộng IELTS",
        "opt_comparison": "📊 Các phương thức khả thi khác:",
        "ueh_title": "🏛️ Đại học Kinh tế TP. Hồ Chí Minh (UEH)",
        "hcmut_title": "🏛️ Đại học Bách Khoa - ĐHQG TP.HCM",
        "ftu_title": "🏛️ Đại học Ngoại Thương (FTU)",
        "hust_title": "🏛️ Đại học Bách Khoa Hà Nội (HUST)",
        "direct_admission_eligible": "✅ **Đủ điều kiện Xét tuyển thẳng**",
        "no_awards": "Không có",
        "first_prize": "Giải Nhất",
        "second_prize": "Giải Nhì",
        "third_prize": "Giải Ba",
        "cons_prize": "Giải Khuyến Khích",
        "cons_prize_national": "Giải Khuyến Khích / Đội tuyển",
        "lang_switch": "🌐 Ngôn ngữ / Language",
        
        "ueh_method2_title": "Phương thức 2 - Xét tuyển tích hợp (Thang 100)",
        "ueh_warn_empty": "⚠️ UEH: Nhập đủ Điểm thi (THPT hoặc ĐGNL V-ACT) và GPA THPT.",
        "hcmut_method2_title": "Phương thức 2 - Xét tuyển Tổng hợp (Thang 100)",
        "hcmut_warn_empty": "⚠️ BK TPHCM: Nhập đủ Học bạ (Toán, Anh, Môn 3) và Thi THPT / V-ACT / SAT.",
        "ftu_method_title": "Xét tuyển ĐH Ngoại Thương (Thang 30 & Thang 40)",
        "ftu_warn_empty": "⚠️ FTU: Chưa đủ thông tin hoặc chưa đạt ngưỡng sàn xét tuyển.",
        "hust_method100_title": "Xét tuyển Talent & ĐGTD (Thang 100)",
        "hust_warn_100_empty": "⚠️ HUST: Chưa đủ thông tin hoặc chưa đạt điều kiện xét tuyển Thang 100.",
        "hust_method30_title": "Phương thức Thi Tốt nghiệp THPT (Thang 30)",
        "hust_warn_30_empty": "*(Chưa nhập đủ điểm thi THPT)*",
        "hust_thpt_score_label": "• **Điểm Xét Tuyển THPT:**",
        
        "lbl_exam_source": "Nguồn điểm thi (60%)",
        "lbl_gpa_thpt": "GPA THPT (40%)",
        "lbl_bonus_pts": "Điểm cộng",
        "lbl_priority_pts": "Điểm ưu tiên",
        "lbl_aptitude_used": "Năng lực sử dụng",
        "lbl_thpt_exam_20": "Thi THPT (20%)",
        "lbl_gpa_10": "GPA (10%)",
        "lbl_method_detail": "Chi tiết phương thức",
        "lbl_scale_30": "Thang 30",
        "lbl_scale_100": "Thang 100",
        "lbl_scale_40": "Thang 40 (KHMT, AI - Toán x2)",
        "lbl_scoring_detail": "Chi tiết tính điểm",
        "lbl_best_tag": "Tốt nhất",
        "pts_unit": "điểm",
        
        "ueh_mth_thpt": "Sử dụng Điểm thi TN THPT",
        "ueh_mth_vact": "Sử dụng ĐGNL V-ACT",
        "hcmut_mth_dt21": "Đối tượng 2.1 (ĐGNL V-ACT)",
        "hcmut_mth_dt24": "Đối tượng 2.4 (Chứng chỉ SAT)",
        "hcmut_mth_dt22": "Đối tượng 2.2 (Thi TN THPT)",
        "ftu_mth_pt3": "PT3 - Điểm thi TN THPT",
        "ftu_mth_pt4_sat": "PT4 - SAT + IELTS",
        "ftu_mth_pt4_hsa": "PT4 - HSA (ĐHQG Hà Nội)",
        "ftu_mth_pt4_vact": "PT4 - V-ACT (ĐHQG TPHCM)",
        "ftu_mth_pt4_tsa": "PT4 - TSA (BK Hà Nội)",
        "hust_mth_12": "XTTN 1.2 (SAT + IELTS)",
        "hust_mth_13": "XTTN 1.3 (Hồ sơ năng lực)",
        "hust_mth_tsa": "Thi ĐGTD (TSA)",

        "pdf_header": "KADEN UNILOOK - KẾT QUẢ ĐIỂM XÉT TUYỂN ĐẠI HỌC THEO ĐỀ ÁN 2026",
        "pdf_footer": "Nguồn: Ứng dụng tra cứu kết quả Xét tuyển Đại học 2026 - Copyright by Kaden UniLook",
        "pdf_sec1": "I. THÔNG TIN HỒ SƠ ỨNG VIÊN",
        "pdf_personal_info": "Thông tin cá nhân:",
        "pdf_certs_tests": "Chứng chỉ quốc tế & Kỳ thi ĐGNL / ĐGTD:",
        "pdf_achievements": "Thành tích & Học sinh giỏi:",
        "pdf_gpa_scores": "Điểm Học bạ THPT (GPA):",
        "pdf_thpt_scores": "Điểm Thi Tốt Nghiệp THPT 2026 & Ưu tiên:",
        "pdf_sec2": "II. KẾT QUẢ XÉT TUYỂN DỰ KIẾN TẠI CÁC TRƯỜNG ĐẠI HỌC",
        "pdf_yes": "Có",
        "pdf_no": "Không",
        "pdf_best_tag": "[TỐI ƯU NHẤT]",
        "pdf_insufficient": "• Chưa đủ thông tin hoặc chưa đạt điều kiện xét tuyển.",
        "pdf_hust_thpt": "• Phương thức Thi TN THPT",
        "pdf_ueh_hdr": "1. Đại học Kinh tế TP. Hồ Chí Minh (UEH) - Thang 100",
        "pdf_hcmut_hdr": "2. Đại học Bách Khoa TPHCM (HCMUT) - Thang 100",
        "pdf_ftu_hdr": "3. Đại học Ngoại Thương (FTU) - Thang 30 & Thang 40",
        "pdf_hust_hdr": "4. Đại học Bách Khoa Hà Nội (HUST) - Thang 100 & Thang 30",

        "um_enable_email": "📧 Bật tính năng gửi email thông báo tự động cho Guest",
        "um_tab_create": "➕ Tạo tài khoản Guest mới",
        "um_tab_list": "📋 Danh sách người dùng",
        "um_tab_actions": "⚡ Khóa/Xóa/Gia hạn tài khoản",
        "um_new_user": "Tên đăng nhập mới",
        "um_new_email": "Email nhận thông báo (Bắt buộc cho Guest)",
        "um_new_fullname": "Họ và tên người dùng",
        "um_new_pass": "Mật khẩu",
        "um_plan_duration": "Gói thời hạn sử dụng",
        "um_btn_create": "Tạo tài khoản Guest",
        "um_err_fill": "Vui lòng điền đầy đủ Tên đăng nhập và Mật khẩu!",
        "um_err_email_req": "❌ Email là thông tin BẮT BUỘC đối với tài khoản Guest!",
        "um_err_email_invalid": "❌ Email không hợp lệ!",
        "um_err_user_exists": "Tên đăng nhập đã tồn tại!",
        "um_success_create": "Đã lưu tài khoản Guest `{}` thành công!",
        "um_err_save": "Ghi thất bại! Kiểm tra quyền Edit trên Google Sheet.",
        "um_col_user": "Tên đăng nhập",
        "um_col_name": "Họ tên",
        "um_col_email": "Email",
        "um_col_role": "Vai trò",
        "um_col_exp": "Hạn sử dụng",
        "um_col_status": "Trạng thái",
        "um_status_suspended": "⛔ TẠM NGƯNG",
        "um_status_active": "Hoạt động",
        "um_status_expired": "⚠️ HẾT HẠN (Cần gia hạn)",
        "um_status_perm": "Vĩnh viễn",
        "um_select_user": "Chọn tài khoản cần thao tác",
        "um_sec_renew": "⏳ Gia hạn tài khoản",
        "um_lbl_account": "Tài khoản",
        "um_lbl_name": "Họ tên",
        "um_lbl_email": "Email",
        "um_renew_plan": "Gói gia hạn mới (Tính từ hôm nay)",
        "um_btn_renew": "🔄 GIA HẠN NGAY",
        "um_success_renew": "Đã gia hạn thành công cho `{}`!",
        "um_sec_lock_del": "⚙️ Khóa hoặc Xóa tài khoản",
        "um_btn_suspend": "🔴 TẠM NGƯNG HOẠT ĐỘNG",
        "um_btn_activate": "🟢 KÍCH HOẠT LẠI",
        "um_btn_delete": "🗑️ XÓA TÀI KHOẢN VĨNH VIỄN",
        "um_no_guests": "Hiện không có tài khoản Guest nào trong hệ thống.",
        "um_dur_1day": "1 ngày",
        "um_dur_1week": "1 tuần",
        "um_dur_1month": "1 tháng",
        "um_dur_6months": "6 tháng",
        "um_dur_1year": "1 năm",
        
        "analysis_sec_title": "📊 PHÂN TÍCH & TƯ VẤN",
        "analysis_attr_label": "📊 THUỘC TÍNH NGÀNH HỌC QUAN TÂM",
        "tab_calculation": "TÍNH TOÁN ĐIỂM XÉT TUYỂN",
        "tab_analysis": "PHÂN TÍCH & TƯ VẤN",
        "tab_user_management": "QUẢN LÝ NGƯỜI DÙNG",
        "analysis_btn": "Phân tích",
        "analysis_table_title": "Danh sách các chương trình/ngành thuộc nhóm \"{}\"",
        "analysis_searching": "Đang tìm kiếm dữ liệu chương trình/ngành học...",
        "analysis_no_data": "Không tìm thấy dữ liệu phù hợp với thuộc tính đã chọn.",
        "analysis_file_err": "❌ Không thể tải tệp dữ liệu 'DH_2026.xlsx' từ Github repository hoặc file local!",
        "analysis_btn_export_excel": "📥 XUẤT BẢNG PHÂN TÍCH RA EXCEL (.XLSX)",
        "analysis_col_no": "STT",
        "analysis_col_school": "Tên trường",
        "analysis_col_major": "Tên ngành",
        "analysis_col_code": "Mã ngành",
        "analysis_col_score": "Điểm chuẩn",
        "analysis_col_method": "Phương thức xét tuyển",
        "analysis_attr_ai": "Trí tuệ nhân tạo (AI) trong kinh doanh",
        "analysis_attr_ds": "Khoa học dữ liệu (DS) trong kinh doanh",
        "analysis_attr_da": "Phân tích dữ liệu (DA) trong kinh doanh",
        "analysis_attr_cs": "Khoa học máy tính (CS) trong kinh doanh",
        "analysis_attr_english": "AI, DS, DA, CS trong kinh doanh - Giảng dạy & học tập bằng Tiếng Anh",
        "analysis_attr_english_match": "Tiếng Anh",
        "analysis_school_ueh": "Đại học Kinh tế TP. Hồ Chí Minh",
        "analysis_school_hcmut": "Đại học Bách Khoa - ĐHQG TP.HCM",
        "analysis_school_ftu": "Đại học Ngoại Thương",
        "analysis_school_hust": "Đại học Bách Khoa Hà Nội",
        "analysis_method_fallback": "Phương thức xét tuyển",
        "analysis_correlation_name": "📊 SO SÁNH TƯƠNG QUAN VỚI ĐIỂM XÉT TUYỂN",
        "analysis_correlation_prompt": "Lọc các ngành có Điểm chuẩn: [Điểm xét tuyển của bạn - **M**] ≤ Điểm chuẩn ≤ [Điểm xét tuyển của bạn + **N**]",
        "analysis_correlation_m": "M (1 - 20)",
        "analysis_correlation_n": "N (1 - 20)",
        "analysis_correlation_btn": "Lọc ngành",
        "analysis_correlation_invalid": "⚠️ M và N phải là số tự nhiên từ 1 đến 20.",
        "analysis_correlation_need_scores": "⚠️ Bạn cần nhập đầy đủ thông số xét tuyển để tính được Điểm xét tuyển cho cả 4 trường UEH, BK TPHCM, FTU và BKHN.",
        "analysis_correlation_need_analysis": "⚠️ Bạn cần thực hiện Phân tích thuộc tính để tạo bảng danh sách các ngành quan tâm trước khi lọc ngành.",
        "analysis_correlation_need_mn": "⚠️ Bạn cần nhập đầy đủ M và N để có điều kiện lọc ngành.",
        "analysis_correlation_no_result": "Không có ngành nào phù hợp với điều kiện tương quan M - N.",
        "analysis_correlation_title": "Danh sách ngành học phục vụ đặt nguyện vọng xét tuyển ưu tiên",
        "toast_email_invalid": "⚠️ Email người nhận không hợp lệ ({}) .",
        "toast_smtp_missing": "⚠️ Chưa cấu hình [smtp] password trong Secrets.",
        "toast_email_sent": "📧 Đã gửi email thông báo tới `{}`!",
        "toast_email_failed": "⚠️ Không thể gửi email tới `{}`: {}",
        "gsheet_conn_error": "⚠️ Lỗi kết nối Google Sheets: {}",
        "gsheet_no_connection": "❌ Không kết nối được với Google Sheets.",
        "gsheet_save_error": "Lỗi ghi dữ liệu lên Google Sheets: {}",
        "pdf_error": "Lỗi PDF: {}",
        "expired_banner": "🚨 **THÔNG BÁO TÀI KHOẢN HẾT HẠN SỬ DỤNG**",
        "expired_message": "Tài khoản của bạn đã hết hạn. Vui lòng liên hệ Admin qua email `{}` để gia hạn.",
        "toast_suspend": "Đã khóa tài khoản `{}`!",
        "toast_activate": "Đã kích hoạt lại `{}`!",
        "toast_delete": "Đã xóa vĩnh viễn tài khoản `{}`!",
        "method_detail_math": "Toán",
        "method_detail_sub3": "Môn 3",
        "method_detail_eng": "Eng",
        "method_detail_bonus": "Điểm cộng IELTS",
        "method_detail_thinking": "Tư duy",
        "method_detail_awards": "Thành tích",
        "method_detail_ut": "UT"
    },
    "en": {
        "page_title": "🎓 UNIVERSITY ADMISSION METHODS CHECKER 2026",
        "page_subtitle": "Comprehensive evaluation & scoring system for UEH - HCMUT - FTU - HUST",
        "login_header": "🔐 SYSTEM LOGIN",
        "login_user": "Username",
        "login_pass": "Password",
        "login_btn": "Sign In",
        "login_checking": "Verifying credentials...",
        "login_err_inactive": "Your account has been SUSPENDED!",
        "login_err_pass": "Incorrect password!",
        "login_err_notfound": "Account not found or connection failed!",
        "login_welcome": "Login successful! Welcome ",
        "login_warning": "⚠️ **ADMISSION SCORE CALCULATION SYSTEM FOR UEH - HCMUT - FTU - HUST**\n\n*Please login to continue using the service*",
        "logout_btn": "Sign Out",
        "expired_title": "⏰ Account EXPIRED on:\n",
        "valid_until": "⏳ Valid until:\n",
        "btn_export": "📄 EXPORT RESULT",
        "btn_admin_mgmt": "⚙️ User Management",
        "sec_applicant": "📋 APPLICANT INFORMATION",
        "fullname": "Full Name",
        "cccd": "ID / Passport Number",
        "sec_exam": "1. Aptitude Test / International Certificates",
        "sec_achieve": "2. Academic Achievements & Awards",
        "sec_gpa": "3. High School GPA (3 Years)",
        "sec_thpt": "4. National High School Exam Scores 2026",
        "sat_label": "SAT Score (0 - 1600)",
        "ielts_label": "IELTS Academic (0 - 9.0)",
        "vact_label": "V-ACT Score (HCM National Univ: 0 - 1200)",
        "hsa_label": "HSA Score (HN National Univ: 0 - 150)",
        "tsa_label": "TSA Score (HUST Thinking Test: 0 - 100)",
        "chuyen_label": "Specialized High School Student (3 Years)",
        "hsg_tinh_label": "Provincial Academic Award",
        "hsg_quocgia_label": "National Academic Award",
        "gpa_math": "Mathematics GPA",
        "gpa_eng": "English GPA",
        "gpa_sub3": "3rd Subject GPA (Phys/Chem/Lit/...)",
        "gpa_avg": "Overall High School GPA",
        "thpt_math": "High School Exam Math Score",
        "thpt_eng": "High School Exam English Score",
        "thpt_sub3": "High School Exam 3rd Subject Score",
        "priority_score": "Priority Bonus Points (30-scale)",
        "opt_best": "BEST OPTIMAL RESULT",
        "opt_score": "Optimal Admission Score",
        "score_with_ielts_bonus": "Including IELTS Bonus",
        "score_without_ielts_bonus": "Excluding IELTS Bonus",
        "opt_comparison": "📊 Other feasible methods:",
        "ueh_title": "🏛️ University of Economics HCMC (UEH)",
        "hcmut_title": "🏛️ HCMUT - VNUHCM",
        "ftu_title": "🏛️ Foreign Trade University (FTU)",
        "hust_title": "🏛️ Hanoi University of Science and Tech (HUST)",
        "direct_admission_eligible": "✅ **Eligible for Direct Admission**",
        "no_awards": "None",
        "first_prize": "1st Prize",
        "second_prize": "2nd Prize",
        "third_prize": "3rd Prize",
        "cons_prize": "Consolation Prize",
        "cons_prize_national": "Consolation Prize / National Team",
        "lang_switch": "🌐 Ngôn ngữ / Language",
        
        "ueh_method2_title": "Method 2 - Integrated Admission (100-pt Scale)",
        "ueh_warn_empty": "⚠️ UEH: Please enter High School Exam or V-ACT scores and overall GPA.",
        "hcmut_method2_title": "Method 2 - Comprehensive Admission (100-pt Scale)",
        "hcmut_warn_empty": "⚠️ HCMUT: Please enter GPA (Math, Eng, 3rd sub) and Exam scores (THPT / V-ACT / SAT).",
        "ftu_method_title": "FTU Admission (Parallel 30-pt & 40-pt Scales)",
        "ftu_warn_empty": "⚠️ FTU: Insufficient information or minimum eligibility score not met.",
        "hust_method100_title": "HUST Talent & TSA Admission (100-pt Scale)",
        "hust_warn_100_empty": "⚠️ HUST: Insufficient information or 100-pt scale requirements not met.",
        "hust_method30_title": "National High School Exam Method (30-pt Scale)",
        "hust_warn_30_empty": "*(High School Exam scores not fully provided)*",
        "hust_thpt_score_label": "• **THPT Admission Score:**",
        
        "lbl_exam_source": "Exam score source (60%)",
        "lbl_gpa_thpt": "High School GPA (40%)",
        "lbl_bonus_pts": "Bonus points",
        "lbl_priority_pts": "Priority points",
        "lbl_aptitude_used": "Aptitude score used",
        "lbl_thpt_exam_20": "THPT Exam (20%)",
        "lbl_gpa_10": "GPA (10%)",
        "lbl_method_detail": "Method breakdown",
        "lbl_scale_30": "30-pt Scale",
        "lbl_scale_100": "100-pt Scale",
        "lbl_scale_40": "40-pt Scale (CS, AI - Math x2)",
        "lbl_scoring_detail": "Scoring breakdown",
        "lbl_best_tag": "Best",
        "pts_unit": "pts",
        
        "ueh_mth_thpt": "High School Exam Score",
        "ueh_mth_vact": "V-ACT Aptitude Test",
        "hcmut_mth_dt21": "Category 2.1 (V-ACT Aptitude)",
        "hcmut_mth_dt24": "Category 2.4 (SAT Certificate)",
        "hcmut_mth_dt22": "Category 2.2 (High School Exam)",
        "ftu_mth_pt3": "Method 3 - High School Exam",
        "ftu_mth_pt4_sat": "Method 4 - SAT + IELTS",
        "ftu_mth_pt4_hsa": "Method 4 - HSA (VNU Hanoi)",
        "ftu_mth_pt4_vact": "Method 4 - V-ACT (VNU HCM)",
        "ftu_mth_pt4_tsa": "Method 4 - TSA (HUST)",
        "hust_mth_12": "Talent Admission 1.2 (SAT + IELTS)",
        "hust_mth_13": "Talent Admission 1.3 (Competency Profile)",
        "hust_mth_tsa": "TSA Aptitude Test",

        "pdf_header": "KADEN UNILOOK - ADMISSION ELIGIBILITY EVALUATION 2026",
        "pdf_footer": "Source: University Admission Checker App 2026 - Copyright by Kaden UniLook",
        "pdf_sec1": "I. APPLICANT PROFILE INFORMATION",
        "pdf_personal_info": "Personal Details:",
        "pdf_certs_tests": "International Certificates & Aptitude Tests:",
        "pdf_achievements": "Academic Achievements & Awards:",
        "pdf_gpa_scores": "High School GPA:",
        "pdf_thpt_scores": "National High School Exam 2026 & Priority Points:",
        "pdf_sec2": "II. ESTIMATED ADMISSION RESULTS BY UNIVERSITIES",
        "pdf_yes": "Yes",
        "pdf_no": "No",
        "pdf_best_tag": "[BEST OPTIMAL]",
        "pdf_insufficient": "• Insufficient information or minimum eligibility score not met.",
        "pdf_hust_thpt": "• High School Exam Method",
        "pdf_ueh_hdr": "1. University of Economics HCMC (UEH) - 100-pt Scale",
        "pdf_hcmut_hdr": "2. HCMUT - VNUHCM - 100-pt Scale",
        "pdf_ftu_hdr": "3. Foreign Trade University (FTU) - 30-pt & 40-pt Scales",
        "pdf_hust_hdr": "4. Hanoi University of Science and Tech (HUST) - 100-pt & 30-pt Scales",

        "um_enable_email": "📧 Enable automatic notification email sending for Guests",
        "um_tab_create": "➕ Create New Guest Account",
        "um_tab_list": "📋 User List",
        "um_tab_actions": "⚡ Lock/Delete/Renew Account",
        "um_new_user": "New Username",
        "um_new_email": "Notification Email (Required for Guest)",
        "um_new_fullname": "Full Name",
        "um_new_pass": "Password",
        "um_plan_duration": "Usage Plan Duration",
        "um_btn_create": "Create Guest Account",
        "um_err_fill": "Please fill in Username and Password!",
        "um_err_email_req": "❌ Email is REQUIRED for Guest accounts!",
        "um_err_email_invalid": "❌ Invalid email address!",
        "um_err_user_exists": "Username already exists!",
        "um_success_create": "Successfully created Guest account `{}`!",
        "um_err_save": "Save failed! Check Edit permissions on Google Sheet.",
        "um_col_user": "Username",
        "um_col_name": "Full Name",
        "um_col_email": "Email",
        "um_col_role": "Role",
        "um_col_exp": "Expiration Date",
        "um_col_status": "Status",
        "um_status_suspended": "⛔ SUSPENDED",
        "um_status_active": "Active",
        "um_status_expired": "⚠️ EXPIRED (Renewal Required)",
        "um_status_perm": "Permanent",
        "um_select_user": "Select account to manage",
        "um_sec_renew": "⏳ Renew Account",
        "um_lbl_account": "Account",
        "um_lbl_name": "Full Name",
        "um_lbl_email": "Email",
        "um_renew_plan": "New renewal duration (From today)",
        "um_btn_renew": "🔄 RENEW NOW",
        "um_success_renew": "Successfully renewed account `{}`!",
        "um_sec_lock_del": "⚙️ Lock or Delete Account",
        "um_btn_suspend": "🔴 SUSPEND ACCOUNT",
        "um_btn_activate": "🟢 REACTIVATE ACCOUNT",
        "um_btn_delete": "🗑️ DELETE ACCOUNT PERMANENTLY",
        "um_no_guests": "There are currently no Guest accounts in the system.",
        "um_dur_1day": "1 day",
        "um_dur_1week": "1 week",
        "um_dur_1month": "1 month",
        "um_dur_6months": "6 months",
        "um_dur_1year": "1 year",
        
        "analysis_sec_title": "📊 ANALYSIS & CONSULTING",
        "analysis_attr_label": "📊 INDUSTRY ATTRIBUTES OF INTEREST",
        "tab_calculation": "Admission Score Calculation",
        "tab_analysis": "Analysis & Consulting",
        "tab_user_management": "User Management",
        "analysis_btn": "Analyze",
        "analysis_table_title": "List of programs/majors under \"{}\"",
        "analysis_searching": "Searching program/major data...",
        "analysis_no_data": "No matching data found for the selected property.",
        "analysis_file_err": "❌ Could not load 'DH_2026.xlsx' from the GitHub repository or local file!",
        "analysis_btn_export_excel": "📥 EXPORT ANALYSIS TABLE TO EXCEL (.XLSX)",
        "analysis_col_no": "No.",
        "analysis_col_school": "University",
        "analysis_col_major": "Major",
        "analysis_col_code": "Major Code",
        "analysis_col_score": "Admission Score",
        "analysis_col_method": "Admission Method",
        "analysis_attr_ai": "Artificial Intelligence (AI) in Business",
        "analysis_attr_ds": "Data Science (DS) in Business",
        "analysis_attr_da": "Data Analytics (DA) in Business",
        "analysis_attr_cs": "Computer Science (CS) in Business",
        "analysis_attr_english": "AI, DS, DA, CS in Business - English-medium Teaching & Learning",
        "analysis_attr_english_match": "English",
        "analysis_school_ueh": "University of Economics Ho Chi Minh City",
        "analysis_school_hcmut": "Ho Chi Minh City University of Technology - VNUHCM",
        "analysis_school_ftu": "Foreign Trade University",
        "analysis_school_hust": "Hanoi University of Science and Technology",
        "analysis_method_fallback": "Admission Method",
        "analysis_correlation_name": "📊 COMPARE RELATIVE TO YOUR ADMISSION SCORE",
        "analysis_correlation_prompt": "Filter majors where: [Your Admission Score - **M**] ≤ Admission Score ≤ [Your Admission Score + **N**]",
        "analysis_correlation_m": "M (1 - 20)",
        "analysis_correlation_n": "N (1 - 20)",
        "analysis_correlation_btn": "Filter Majors",
        "analysis_correlation_invalid": "⚠️ M and N must be natural numbers from 1 to 20.",
        "analysis_correlation_need_scores": "⚠️ You need to enter sufficient admission information to calculate an admission score for all 4 universities: UEH, HCMUT, FTU and HUST.",
        "analysis_correlation_need_analysis": "⚠️ You need to run the attribute analysis first to create the list of majors of interest before filtering.",
        "analysis_correlation_need_mn": "⚠️ You need to enter both M and N to define the filtering condition.",
        "analysis_correlation_no_result": "No majors match the M - N relative condition.",
        "analysis_correlation_title": "Majors list for priority admission preference planning",
        "toast_email_invalid": "⚠️ Invalid recipient email ({}) .",
        "toast_smtp_missing": "⚠️ SMTP password is not configured in Secrets.",
        "toast_email_sent": "📧 Notification email sent to `{}`!",
        "toast_email_failed": "⚠️ Could not send email to `{}`: {}",
        "gsheet_conn_error": "⚠️ Google Sheets connection error: {}",
        "gsheet_no_connection": "❌ Could not connect to Google Sheets.",
        "gsheet_save_error": "Failed to save data to Google Sheets: {}",
        "pdf_error": "PDF error: {}",
        "expired_banner": "🚨 **ACCOUNT EXPIRATION NOTICE**",
        "expired_message": "Your account has expired. Please contact Admin via email `{}` to renew it.",
        "toast_suspend": "Account `{}` has been suspended!",
        "toast_activate": "Account `{}` has been reactivated!",
        "toast_delete": "Account `{}` has been permanently deleted!",
        "method_detail_math": "Math",
        "method_detail_sub3": "Sub3",
        "method_detail_eng": "English",
        "method_detail_bonus": "IELTS Bonus",
        "method_detail_thinking": "Thinking",
        "method_detail_awards": "Awards",
        "method_detail_ut": "Priority"
    }
}

if "lang" not in st.session_state:
    st.session_state.lang = "vi"

if "hsg_tinh_idx" not in st.session_state:
    st.session_state.hsg_tinh_idx = 0

if "hsg_quocgia_idx" not in st.session_state:
    st.session_state.hsg_quocgia_idx = 0

GITHUB_DH_2026_XLSX_URL = "https://raw.githubusercontent.com/kadentran/kadenunilook/main/DH_2026.xlsx"
GITHUB_DH_2026_CSV_URL = "https://raw.githubusercontent.com/kadentran/kadenunilook/main/DH_2026.csv"

# ---------------------------------------------------------
# CẤU HÌNH & HÀM GỬI EMAIL TỰ ĐỘNG (SMTP)
# ---------------------------------------------------------
SENDER_EMAIL = "kadentran690@gmail.com"

def is_valid_email(email_str):
    if not email_str or not isinstance(email_str, str):
        return False
    email_str = email_str.strip().lower()
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email_str))

def get_smtp_password():
    try:
        if "smtp" in st.secrets and "password" in st.secrets["smtp"]:
            return st.secrets["smtp"]["password"]
        if "smtp_password" in st.secrets:
            return st.secrets["smtp_password"]
        if "smtp.password" in st.secrets:
            return st.secrets["smtp.password"]
        if "SMTP_PASSWORD" in os.environ:
            return os.environ["SMTP_PASSWORD"]
    except Exception:
        pass
    return None

def send_notification_email(receiver_email, subject, body_content, enable_email=True):
    if not enable_email:
        return False
    if not is_valid_email(receiver_email):
        st.toast(t["toast_email_invalid"].format(receiver_email), icon="⚠️")
        return False

    smtp_password = get_smtp_password()
    if not smtp_password:
        st.toast(t["toast_smtp_missing"], icon="⚠️")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body_content, 'plain', 'utf-8'))

        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.starttls()
        server.login(SENDER_EMAIL, smtp_password)
        server.send_message(msg)
        server.quit()
        st.toast(t["toast_email_sent"].format(receiver_email), icon="🚀")
        return True
    except Exception as e:
        st.toast(t["toast_email_failed"].format(receiver_email, e), icon="⚠️")
        return False

# ---------------------------------------------------------
# KẾT NỐI VÀ QUẢN LÝ DỮ LIỆU TÀI KHOẢN QUA GSPREAD
# ---------------------------------------------------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource(ttl=300)
def get_gspread_client():
    try:
        if "gcp_service_account" in st.secrets:
            creds = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"], scopes=SCOPES
            )
        elif os.path.exists("service_account.json"):
            creds = Credentials.from_service_account_file(
                "service_account.json", scopes=SCOPES
            )
        else:
            return None
        return gspread.authorize(creds)
    except Exception:
        return None

def get_worksheet():
    gc = get_gspread_client()
    if gc is None:
        return None
    try:
        sheet_url_or_id = st.secrets.get("connections", {}).get("gsheets", {}).get("spreadsheet", None)
        if sheet_url_or_id:
            sh = gc.open_by_url(sheet_url_or_id) if sheet_url_or_id.startswith("http") else gc.open_by_key(sheet_url_or_id)
        else:
            sh = gc.open("UserDB")
        return sh.sheet1
    except Exception:
        return None

@st.cache_data(ttl=60, show_spinner=False)
def load_users_from_gsheets():
    worksheet = get_worksheet()
    if worksheet is None:
        return {}
    try:
        records = worksheet.get_all_records()
        if not records:
            return {}
        df = pd.DataFrame(records)
        df['is_active'] = df['is_active'].astype(str).str.upper() == 'TRUE'
        
        if 'email' not in df.columns:
            df['email'] = ""

        users_dict = {}
        for _, row in df.iterrows():
            val_exp = str(row['expire_date']).strip()
            expire_val = None if val_exp.lower() in ['none', 'nan', '', 'null'] else val_exp
            email_val = str(row['email']).strip()
            if email_val.lower() in ['none', 'nan', 'null']: email_val = ""

            users_dict[str(row['username'])] = {
                "password": str(row['password']),
                "role": str(row['role']),
                "full_name": str(row['full_name']),
                "email": email_val,
                "expire_date": expire_val,
                "is_active": row['is_active']
            }
        return users_dict
    except Exception as e:
        st.error(t["gsheet_conn_error"].format(e))
        return {}

def save_users_to_gsheets(users_dict):
    worksheet = get_worksheet()
    if worksheet is None:
        st.error(t["gsheet_no_connection"])
        return False
    try:
        data = []
        for u, d in users_dict.items():
            data.append({
                "username": u,
                "password": d["password"],
                "role": d["role"],
                "full_name": d["full_name"],
                "email": d.get("email", ""),
                "expire_date": str(d["expire_date"]) if d["expire_date"] else "None",
                "is_active": "TRUE" if d["is_active"] else "FALSE"
            })
        df_new = pd.DataFrame(data)
        worksheet.clear()
        worksheet.update(range_name='A1', values=[df_new.columns.values.tolist()] + df_new.values.tolist())
        load_users_from_gsheets.clear()
        return True
    except Exception as e:
        st.error(t["gsheet_save_error"].format(e))
        return False

# ---------------------------------------------------------
# HÀM LẤY DỮ LIỆU TỪ TẤT CẢ CÁC SHEET CỦA "DH_2026.xlsx"
# ---------------------------------------------------------
@st.cache_data(ttl=300, show_spinner=False)
def load_dh_2026_data():
    try:
        r = requests.get(GITHUB_DH_2026_XLSX_URL, timeout=10)
        if r.status_code == 200:
            excel_file = pd.ExcelFile(io.BytesIO(r.content), engine="openpyxl")
            dfs = [excel_file.parse(sheet_name) for sheet_name in excel_file.sheet_names]
            return pd.concat(dfs, ignore_index=True)
    except Exception:
        pass
    try:
        r = requests.get(GITHUB_DH_2026_CSV_URL, timeout=10)
        if r.status_code == 200:
            return pd.read_csv(io.StringIO(r.content.decode('utf-8')))
    except Exception:
        pass
    for f in ["DH_2026.xlsx", "DH 2026.xlsx", "DH_2026.csv", "DH 2026.csv"]:
        if os.path.exists(f):
            try:
                if f.endswith(".xlsx"):
                    excel_file = pd.ExcelFile(f, engine="openpyxl")
                    dfs = [excel_file.parse(sheet_name) for sheet_name in excel_file.sheet_names]
                    return pd.concat(dfs, ignore_index=True)
                else:
                    return pd.read_csv(f)
            except Exception:
                pass
    return None

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if "show_user_mgmt_modal" not in st.session_state:
    st.session_state.show_user_mgmt_modal = False

if "enable_email_notify" not in st.session_state:
    st.session_state.enable_email_notify = True

st.markdown(f"""
    <style>
    /* Bản quyền được cố định tại góc dưới cùng bên phải của ứng dụng.
       Tách thành 2 dòng và dùng chữ đậm theo yêu cầu. */
    .copyright-header {{
        position: fixed;
        right: 10px;
        bottom: 8px;
        font-size: 13px;
        line-height: 1.35;
        color: #6c757d;
        font-weight: 700;
        text-align: right;
        white-space: nowrap;
        z-index: 99999;
        background-color: rgba(255, 255, 255, 0.88);
        padding: 3px 6px;
        border-radius: 4px;
    }}

    /* Đưa toàn bộ nội dung chính sát mép trên màn hình hơn sau khi
       loại bỏ dòng bản quyền ở phía trên. */
    section.main > div.block-container {{
        padding-top: 0.35rem !important;
    }}

    section.main > div.block-container > div {{
        padding-top: 0 !important;
    }}
    
    /* ---------------------------------------------------------
       ĐỒNG BỘ MÀU CHO TOÀN BỘ NÚT LỆNH
       Màu chuẩn: Bordeaux / Dark Burgundy, đồng nhất với nút
       "XUẤT KẾT QUẢ" hiện có.
       --------------------------------------------------------- */
    div.stButton > button,
    div[data-testid="stDownloadButton"] > button,
    div[data-testid="stFormSubmitButton"] > button,
    div[data-testid="stFormSubmitButton"] button,
    div.element-container:has(button[key="btn_admin_mgmt"]) button,
    div.element-container:has(button[key="btn_admin_mgmt_active"]) button {{
        background-color: #8B0000 !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: 1px solid #700000 !important;
        padding: 0.4rem 1rem !important;
        transition: all 0.3s ease;
    }}

    div.stButton > button:hover,
    div[data-testid="stDownloadButton"] > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover,
    div[data-testid="stFormSubmitButton"] button:hover,
    div.element-container:has(button[key="btn_admin_mgmt"]) button:hover,
    div.element-container:has(button[key="btn_admin_mgmt_active"]) button:hover {{
        background-color: #B22222 !important;
        color: #FFFFFF !important;
        border-color: #B22222 !important;
    }}

    div.stButton > button:active,
    div.stButton > button:focus,
    div[data-testid="stDownloadButton"] > button:active,
    div[data-testid="stDownloadButton"] > button:focus,
    div[data-testid="stFormSubmitButton"] > button:active,
    div[data-testid="stFormSubmitButton"] > button:focus,
    div[data-testid="stFormSubmitButton"] button:active,
    div[data-testid="stFormSubmitButton"] button:focus,
    div.element-container:has(button[key="btn_admin_mgmt_active"]) button:active,
    div.element-container:has(button[key="btn_admin_mgmt_active"]) button:focus {{
        background-color: #DC143C !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: 2px solid #FF4500 !important;
        padding: 0.4rem 1rem !important;
        box-shadow: 0 0 10px rgba(220, 20, 60, 0.6) !important;
    }}

    /* Nút bị disabled vẫn giữ đúng tông Bordeaux, chỉ giảm độ tương phản. */
    div.stButton > button:disabled,
    div[data-testid="stDownloadButton"] > button:disabled,
    div[data-testid="stFormSubmitButton"] > button:disabled,
    div[data-testid="stFormSubmitButton"] button:disabled {{
        background-color: #8B0000 !important;
        color: #FFFFFF !important;
        border-color: #700000 !important;
        opacity: 0.65 !important;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-top: 4px solid #2563eb !important;
        border-radius: 14px !important;
        padding: 18px !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01) !important;
        transition: all 0.3s ease-in-out !important;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
        border-color: #cbd5e1 !important;
        box-shadow: 0 20px 30px -10px rgba(0, 0, 0, 0.09) !important;
        transform: translateY(-2px);
    }}

    .optimal-badge {{
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background-color: #dcfce7;
        color: #15803d;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 3px 12px;
        border-radius: 16px;
        border: 1px solid #bbf7d0;
        margin-top: 6px;
        margin-bottom: 12px;
    }}

    .opt-score-display {{
        font-size: 2.2rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.15;
    }}

    div[data-baseweb="tab-panel"] {{
        padding-top: 0.35rem !important;
    }}

    /* Tiêu đề các Tab chính: chữ hoa và in đậm. */
    div[data-baseweb="tab-list"] button[data-baseweb="tab"] {{
        font-weight: 700 !important;
        text-transform: uppercase !important;
    }}
    div[data-baseweb="tab-list"] button[data-baseweb="tab"] * {{
        font-weight: 700 !important;
    }}
    </style>
    <div class="copyright-header">
        <div>Copyright by Kaden UniLook</div>
        <div>Contact: {SENDER_EMAIL}</div>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# QUẢN LÝ ĐĂNG NHẬP & CHỌN NGÔN NGỮ SIDEBAR
# ---------------------------------------------------------
if os.path.exists("KADEN_logo.png"):
    st.sidebar.image("KADEN_logo.png", use_container_width=True)

def on_lang_change():
    selected = st.session_state.radio_lang_selection
    new_lang = "vi" if "Tiếng Việt" in selected else "en"
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        t_new = TRANS[new_lang]
        hsg_tinh_opts_new = [t_new["no_awards"], t_new["first_prize"], t_new["second_prize"], t_new["third_prize"], t_new["cons_prize"]]
        hsg_quocgia_opts_new = [t_new["no_awards"], t_new["first_prize"], t_new["second_prize"], t_new["third_prize"], t_new["cons_prize_national"]]
        
        idx_t = min(st.session_state.hsg_tinh_idx, len(hsg_tinh_opts_new) - 1)
        st.session_state["val_hsg_tinh"] = hsg_tinh_opts_new[idx_t]
        
        idx_q = min(st.session_state.hsg_quocgia_idx, len(hsg_quocgia_opts_new) - 1)
        st.session_state["val_hsg_quocgia"] = hsg_quocgia_opts_new[idx_q]

if "radio_lang_selection" not in st.session_state:
    st.session_state["radio_lang_selection"] = "🇻🇳 Tiếng Việt" if st.session_state.lang == "vi" else "🇬🇧 English"

selected_lang_label = st.sidebar.radio(
    "🌐 Ngôn ngữ / Language",
    options=["🇻🇳 Tiếng Việt", "🇬🇧 English"],
    horizontal=True,
    key="radio_lang_selection",
    on_change=on_lang_change
)

t = TRANS[st.session_state.lang]

st.sidebar.title(t["login_header"])

if st.session_state.logged_in_user is None:
    username_input = st.sidebar.text_input(t["login_user"])
    password_input = st.sidebar.text_input(t["login_pass"], type="password")
    
    if st.sidebar.button(t["login_btn"], use_container_width=True):
        with st.spinner(t["login_checking"]):
            users_db = load_users_from_gsheets()
            st.session_state.users_db = users_db
            
            if username_input in users_db:
                user_info = users_db[username_input]
                if not user_info.get("is_active", True):
                    st.sidebar.error(t["login_err_inactive"])
                elif str(user_info["password"]) == str(password_input):
                    st.session_state.logged_in_user = username_input
                    st.sidebar.success(f"{t['login_welcome']}{user_info['full_name']}")
                    st.rerun()
                else:
                    st.sidebar.error(t["login_err_pass"])
            else:
                st.sidebar.error(t["login_err_notfound"])
    
    col_lead1, col_lead2, col_lead3 = st.columns([1, 3, 1])
    with col_lead2:
        st.write("##")
        st.write("##")
        st.warning(t["login_warning"])
    st.stop()
else:
    if "users_db" not in st.session_state:
        st.session_state.users_db = load_users_from_gsheets()

    current_user = st.session_state.logged_in_user
    if current_user not in st.session_state.users_db:
        st.session_state.logged_in_user = None
        st.rerun()
        
    user_data = st.session_state.users_db[current_user]
    
    if not user_data.get("is_active", True):
        st.session_state.logged_in_user = None
        st.error(f"🚨 {t['login_err_inactive']}")
        st.stop()
    
    st.sidebar.success(f"👤 **{user_data['full_name']}** ({user_data['role'].upper()})")
    
    is_expired = False
    if user_data["role"] == "guest" and user_data["expire_date"]:
        try:
            expire_dt = datetime.strptime(user_data["expire_date"], "%Y-%m-%d %H:%M:%S")
            if datetime.now() > expire_dt:
                is_expired = True
                st.sidebar.error(f"{t['expired_title']}{user_data['expire_date']} (UTC)")
            else:
                st.sidebar.info(f"{t['valid_until']}{user_data['expire_date']} (UTC)")
        except ValueError: