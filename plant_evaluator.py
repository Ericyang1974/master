import streamlit as st
import pandas as pd
from PIL import Image
import base64

st.set_page_config(layout="wide")

# --- Init session state ---
if "features" not in st.session_state:
    st.session_state.features = [
        "Function layout",
        "Material & person flow",
        "Corporate image",
        "Extension possibility",
        "Wind direction & orientation"
    ]

if "options" not in st.session_state:
    st.session_state.options = [{"name": f"Option {i+1}", "desc": "", "image": None} for i in range(3)]

# --- Image Popup Helper ---
def get_image_base64(img):
    if img:
        image = Image.open(img)
        buffered = image.resize((min(1000, image.width), min(700, image.height)))
        from io import BytesIO
        buf = BytesIO()
        buffered.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()

# --- Sticky Header + Style ---
st.markdown("""
    <style>
    .sticky-header {
        position: sticky;
        top: 0;
        background-color: white;
        padding: 1em 0;
        z-index: 999;
        border-bottom: 1px solid #ccc;
    }
    .thumb:hover {
        cursor: pointer;
        transform: scale(1.05);
        transition: 0.3s;
    }
    .popup-img {
        position: fixed;
        top: 5%;
        left: 5%;
        width: 90%;
        max-height: 90%;
        z-index: 1000;
        background-color: rgba(0, 0, 0, 0.85);
        text-align: center;
        padding-top: 40px;
        border-radius: 8px;
    }
    .popup-img img {
        max-height: 80vh;
        max-width: 90%;
    }
    .close-btn {
        position: absolute;
        top: 10px;
        right: 20px;
        font-size: 28px;
        color: red;
        cursor: pointer;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- Mode Switch ---
mode = st.radio("Select Mode", ["Developer Mode", "User Mode"])

# -------------------- Developer Mode --------------------
if mode == "Developer Mode":
    st.title("🛠️ Developer Mode")

    st.header("📋 Project Information")
    st.session_state.client_name = st.text_input("Client Name", value=st.session_state.get("client_name", ""))
    st.session_state.project_name = st.text_input("Project Name", value=st.session_state.get("project_name", ""))
    st.session_state.design_company = st.text_input("Design Company", value=st.session_state.get("design_company", ""))

    st.header("🏗️ Options Configuration")
    num_options = st.number_input("Number of Options", min_value=1, max_value=10, value=len(st.session_state.options))
    if num_options != len(st.session_state.options):
        st.session_state.options = [{"name": f"Option {i+1}", "desc": "", "image": None} for i in range(num_options)]

    for i, opt in enumerate(st.session_state.options):
        st.subheader(f"Option {i+1}")
        opt["name"] = st.text_input("Option Name", value=opt["name"], key=f"opt_name_{i}")
        opt["desc"] = st.text_area("Option Description", value=opt["desc"], key=f"opt_desc_{i}")
        opt["image"] = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"], key=f"opt_img_{i}")

    st.header("📌 Define Evaluation Features")
    new_features = []
    for i, feat in enumerate(st.session_state.features):
        new_feat = st.text_input(f"Feature {i+1}", value=feat, key=f"feat_{i}")
        new_features.append(new_feat)
    st.session_state.features = new_features

# -------------------- User Mode --------------------
else:
    st.title("📊 User Evaluation Mode")

    # Sticky project info
    st.markdown(f"""
    <div class="sticky-header">
        <b>Client:</b> {st.session_state.get('client_name', 'N/A')} |
        <b>Project:</b> {st.session_state.get('project_name', 'N/A')} |
        <b>Design Co.:</b> {st.session_state.get('design_company', 'N/A')}
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📷 Options Overview")
    col_list = st.columns(len(st.session_state.options))
    for i, (col, opt) in enumerate(zip(col_list, st.session_state.options)):
        with col:
            st.markdown(f"**{opt['name']}**", unsafe_allow_html=True)
            if opt["image"] is not None:
                encoded = get_image_base64(opt["image"])
                if encoded:
                    st.markdown(
                        f'<img src="data:image/png;base64,{encoded}" class="thumb" '
                        f'onclick="document.getElementById(\'popup_{i}\').style.display=\'block\'" width="100%"/>',
                        unsafe_allow_html=True
                    )
                    popup_html = f"""
                        <div id="popup_{i}" class="popup-img" style="display:none">
                            <div class="close-btn" onclick="document.getElementById('popup_{i}').style.display='none'">✖</div>
                            <img src="data:image/png;base64,{encoded}">
                        </div>
                    """
                    st.markdown(popup_html, unsafe_allow_html=True)
            else:
                st.write("No image uploaded.")
            st.markdown(f"{opt['desc']}", unsafe_allow_html=True)

    st.header("📌 Features")
    for i, feat in enumerate(st.session_state.features):
        st.markdown(f"**Feature {i+1}:** {feat}")

    st.divider()
    st.info("Evaluator input interface is coming next!")
    st.subheader("👥 Evaluator Input")

    if "evaluations" not in st.session_state:
        st.session_state.evaluations = []

    with st.form("eval_form", clear_on_submit=True):
        name = st.text_input("Evaluator Name")
        st.markdown("### 🧮 Weight Assignment (Total must be 100%)")
        weights = {}
        total_weight = 0
        for feat in st.session_state.features:
            w = st.number_input(f"Weight for '{feat}' (%)", min_value=0, max_value=100, step=1, key=f"{name}_{feat}_weight")
            weights[feat] = w
            total_weight += w

        st.markdown("### ✏️ Score Each Option")
        scores = {}
        for opt in st.session_state.options:
            with st.expander(f"Scores for {opt['name']}"):
                scores[opt["name"]] = {}
                for feat in st.session_state.features:
                    s = st.slider(f"{feat} score", 0, 10, 5, key=f"{name}_{opt['name']}_{feat}_score")
                    scores[opt["name"]][feat] = s

        submitted = st.form_submit_button("Submit Evaluation")
        if submitted:
            if total_weight != 100:
                st.error("⚠️ Total weight must equal 100%. Please adjust and resubmit.")
            elif not name.strip():
                st.error("⚠️ Please enter your name.")
            else:
                st.session_state.evaluations.append({
                    "name": name,
                    "weights": weights,
                    "scores": scores
                })
                st.success(f"✅ Evaluation from {name} submitted!")

    # Final score calculation
    if st.session_state.evaluations:
        st.subheader("📊 Final Evaluation Results")

        # Average weights
        avg_weights = {}
        for feat in st.session_state.features:
            avg_weights[feat] = sum(ev["weights"][feat] for ev in st.session_state.evaluations) / len(st.session_state.evaluations)

        # Average scores
        option_scores = {}
        for opt in st.session_state.options:
            opt_name = opt["name"]
            option_scores[opt_name] = {}
            for feat in st.session_state.features:
                option_scores[opt_name][feat] = sum(ev["scores"][opt_name][feat] for ev in st.session_state.evaluations) / len(st.session_state.evaluations)

        # Final weighted scores
        final_scores = {}
        for opt_name, feat_scores in option_scores.items():
            total = 0
            for feat in st.session_state.features:
                total += feat_scores[feat] * avg_weights[feat] / 100
            final_scores[opt_name] = total

        # Display
        st.markdown("### 🔢 Score Breakdown")
        df_breakdown = pd.DataFrame(option_scores).T
        df_breakdown["Final Weighted Score"] = pd.Series(final_scores)
        df_breakdown = df_breakdown[st.session_state.features + ["Final Weighted Score"]]
        st.dataframe(df_breakdown.style.highlight_max(axis=0, subset=["Final Weighted Score"], color="lightgreen"))

        best_option = max(final_scores, key=final_scores.get)
        st.success(f"🏆 Best Option: **{best_option}** with score **{final_scores[best_option]:.2f}**")
