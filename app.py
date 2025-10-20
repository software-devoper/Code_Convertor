from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
import os
import streamlit as st
import pandas as pd
import time
import json
import pyperclip
from datetime import datetime
import base64

load_dotenv()

API_KEY = os.getenv('OPENROUTER_API_KEY')
os.environ['OPENAI_API_KEY'] = API_KEY
os.environ['OPENAI_API_BASE'] = 'https://openrouter.ai/api/v1'

# Configure page
st.set_page_config(
    page_title="Code Converter Pro",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS for beautiful UI
st.markdown("""
<style>
    /* Main Styles */
    .main-header {
        font-size: 3.5rem;
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1, #96CEB4, #FFE66D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: 800;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
        font-size: 1.2rem;
    }
    
    /* Glassmorphism Cards */
    .converter-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        margin: 15px 0;
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .input-card {
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.15), rgba(78, 205, 196, 0.15));
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    
    .output-card {
        background: linear-gradient(135deg, rgba(79, 172, 254, 0.15), rgba(0, 242, 254, 0.15));
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    
    .stats-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Language Tags */
    .language-tag {
        background: rgba(255,255,255,0.15);
        padding: 8px 16px;
        border-radius: 20px;
        margin: 4px;
        display: inline-block;
        font-weight: 600;
        font-size: 0.8rem;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Buttons */
    .convert-btn {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 15px 40px;
        font-size: 1.1rem;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        margin: 20px 0;
        box-shadow: 0 5px 15px rgba(255, 107, 107, 0.3);
    }
    
    .convert-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
    }
    
    .action-btn {
        background: rgba(255,255,255,0.15);
        color: white;
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 15px;
        padding: 10px 20px;
        margin: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 600;
        font-size: 0.8rem;
    }
    
    .action-btn:hover {
        background: rgba(255,255,255,0.25);
        transform: translateY(-1px);
    }
    
    /* History Items */
    .history-item {
        background: rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 15px;
        margin: 8px 0;
        border-left: 4px solid #4ECDC4;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .history-item:hover {
        background: rgba(255,255,255,0.15);
        transform: translateX(5px);
    }
    
    /* Code Blocks */
    .code-block {
        background: #1e1e1e;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        font-family: 'Courier New', monospace;
        color: #f8f8f2;
        border: 2px solid #333;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .feature-card {
        background: rgba(255,255,255,0.08);
        border-radius: 15px;
        padding: 20px;
        margin: 8px;
        text-align: center;
        transition: all 0.3s ease;
        border: 1px solid rgba(255,255,255,0.1);
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-3px);
        background: rgba(255,255,255,0.12);
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        border-radius: 10px;
    }
    
    /* Fix Streamlit container spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Sidebar improvements */
    .css-1d391kg {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'conversion_history' not in st.session_state:
    st.session_state.conversion_history = []

if 'total_conversions' not in st.session_state:
    st.session_state.total_conversions = 0

if 'favorite_conversions' not in st.session_state:
    st.session_state.favorite_conversions = []

if 'current_code_input' not in st.session_state:
    st.session_state.current_code_input = ""

if 'current_source_lang' not in st.session_state:
    st.session_state.current_source_lang = "python"

if 'current_target_lang' not in st.session_state:
    st.session_state.current_target_lang = "javascript"

if 'converted_code' not in st.session_state:
    st.session_state.converted_code = ""

# Programming languages with icons
LANGUAGES = {
    "python": {"icon": "🐍", "name": "Python", "color": "#3776AB"},
    "javascript": {"icon": "📜", "name": "JavaScript", "color": "#F7DF1E"},
    "java": {"icon": "☕", "name": "Java", "color": "#007396"},
    "c++": {"icon": "⚡", "name": "C++", "color": "#00599C"},
    "c": {"icon": "🔧", "name": "C", "color": "#A8B9CC"},
    "c#": {"icon": "🎵", "name": "C#", "color": "#239120"},
    "php": {"icon": "🐘", "name": "PHP", "color": "#777BB4"},
    "go": {"icon": "🚀", "name": "Go", "color": "#00ADD8"},
    "rust": {"icon": "🦀", "name": "Rust", "color": "#000000"},
    "typescript": {"icon": "📘", "name": "TypeScript", "color": "#3178C6"},
    "r": {"icon": "📊", "name": "R", "color": "#276DC3"},
    "perl": {"icon": "🐪", "name": "Perl", "color": "#39457E"},
    "lua": {"icon": "🌙", "name": "Lua", "color": "#2C2D72"},
    "kotlin": {"icon": "🤖", "name": "Kotlin", "color": "#7F52FF"},
    "swift": {"icon": "🐦", "name": "Swift", "color": "#FA7343"},
    "ruby": {"icon": "💎", "name": "Ruby", "color": "#CC342D"},
    "scala": {"icon": "⚡", "name": "Scala", "color": "#DC322F"},
    "dart": {"icon": "🎯", "name": "Dart", "color": "#00B4AB"}
}

def get_language_display(lang_key):
    """Get formatted language display with icon"""
    lang = LANGUAGES.get(lang_key, {"icon": "❓", "name": lang_key, "color": "#666"})
    return f"{lang['icon']} {lang['name']}"

def detect_language(code):
    """Simple code language detection"""
    if not code or not code.strip():
        return "unknown"
        
    code_lower = code.lower().strip()
    
    detection_patterns = {
        'python': ['def ', 'import ', 'print(', 'elif ', 'lambda ', 'from ', 'numpy', 'pandas'],
        'javascript': ['function ', 'const ', 'let ', 'var ', '=>', 'console.log', 'document.', 'ajax'],
        'java': ['public class', 'void main', 'System.out', 'import java', 'String[] args'],
        'c++': ['#include <iostream>', 'using namespace', 'std::', 'cout <<', 'cin >>'],
        'c': ['#include <stdio.h>', 'printf(', 'scanf(', '#include "', 'int main('],
        'php': ['<?php', '$', 'echo ', 'function ', '$_GET', '$_POST'],
        'go': ['package main', 'import "', 'func main()', 'fmt.Print', 'go func'],
        'rust': ['fn main()', 'let ', 'println!', 'use std::', 'mut ', 'Vec::'],
        'typescript': ['interface ', 'type ', ': string', ': number', 'export const']
    }
    
    for lang, patterns in detection_patterns.items():
        if any(pattern in code_lower for pattern in patterns):
            return lang
    
    return "unknown"

def get_language_info(language):
    """Get information about programming languages"""
    language_info = {
        "python": {"paradigm": "Multi-paradigm", "typing": "Dynamic", "year": 1991},
        "javascript": {"paradigm": "Multi-paradigm", "typing": "Dynamic", "year": 1995},
        "java": {"paradigm": "Object-oriented", "typing": "Static", "year": 1995},
        "c++": {"paradigm": "Multi-paradigm", "typing": "Static", "year": 1985},
        "c": {"paradigm": "Procedural", "typing": "Static", "year": 1972},
        "php": {"paradigm": "Multi-paradigm", "typing": "Dynamic", "year": 1995},
        "go": {"paradigm": "Concurrent", "typing": "Static", "year": 2009},
        "rust": {"paradigm": "Multi-paradigm", "typing": "Static", "year": 2010},
        "typescript": {"paradigm": "Multi-paradigm", "typing": "Static", "year": 2012}
    }
    return language_info.get(language, {"paradigm": "N/A", "typing": "N/A", "year": "N/A"})

def copy_to_clipboard(text):
    """Copy text to clipboard"""
    try:
        pyperclip.copy(text)
        return True
    except:
        return False

def analyze_code_complexity(code):
    """Simple code complexity analysis"""
    if not code:
        return {"total_lines": 0, "non_empty_lines": 0, "comment_lines": 0, "code_lines": 0, "comment_ratio": 0}
        
    lines = code.split('\n')
    total_lines = len(lines)
    non_empty_lines = len([line for line in lines if line.strip()])
    comment_lines = len([line for line in lines if line.strip().startswith(('#', '//', '/*', '*', '--'))])
    
    return {
        "total_lines": total_lines,
        "non_empty_lines": non_empty_lines,
        "comment_lines": comment_lines,
        "code_lines": non_empty_lines - comment_lines,
        "comment_ratio": comment_lines / non_empty_lines if non_empty_lines > 0 else 0
    }

def set_code_template(template_type):
    """Set code templates"""
    templates = {
        "python": """def fibonacci(n):
    # Calculate Fibonacci sequence
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

# Test the function
for i in range(10):
    print(f"Fibonacci({i}) = {fibonacci(i)}")""",
        
        "javascript": """function factorial(n) {
    // Calculate factorial recursively
    if (n === 0 || n === 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

// Test the function
for (let i = 0; i < 10; i++) {
    console.log(`Factorial(${i}) = ${factorial(i)}`);
}""",
        
        "java": """public class Calculator {
    public static int add(int a, int b) {
        return a + b;
    }
    
    public static void main(String[] args) {
        // Test addition
        int result = add(5, 3);
        System.out.println("5 + 3 = " + result);
    }
}"""
    }
    
    return templates.get(template_type, "")

def swap_languages():
    """Swap source and target languages"""
    current_source = st.session_state.current_source_lang
    current_target = st.session_state.current_target_lang
    st.session_state.current_source_lang = current_target
    st.session_state.current_target_lang = current_source

def main():
    # Header
    st.markdown('<h1 class="main-header">💻 Code Converter Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Transform your code between 15+ programming languages with AI-powered precision</p>', unsafe_allow_html=True)
    
    # Initialize model and parser
    parser = StrOutputParser()
    model = ChatOpenAI(
        model='cognitivecomputations/dolphin-mistral-24b-venice-edition:free',
        temperature=0
    )

    # Sidebar - Fixed layout
    with st.sidebar:
        st.markdown("### 📊 Conversion Stats")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div class="stats-card">Total<br><h3>{st.session_state.total_conversions}</h3></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stats-card">History<br><h3>{len(st.session_state.conversion_history)}</h3></div>', unsafe_allow_html=True)
        
        st.markdown("### 🌟 Supported Languages")
        # Display languages in a compact grid
        language_text = ""
        for lang_key, lang_data in LANGUAGES.items():
            language_text += f"{lang_data['icon']} {lang_data['name']}  \n"
        st.markdown(language_text)
        
        st.markdown("---")
        st.markdown("### 📚 Recent Conversions")
        
        if st.session_state.conversion_history:
            for i, item in enumerate(reversed(st.session_state.conversion_history[-3:])):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"""
                        **{LANGUAGES[item['from_lang']]['icon']} → {LANGUAGES[item['to_lang']]['icon']}**
                        """)
                        st.caption(f"{item['timestamp'].split(' ')[1]}")
                    with col2:
                        if st.button("↻", key=f"reload_{i}"):
                            st.session_state.current_code_input = item['input']
                            st.session_state.current_source_lang = item['from_lang']
                            st.session_state.current_target_lang = item['to_lang']
                            st.rerun()
        else:
            st.info("No conversions yet")
        
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.conversion_history = []
            st.session_state.total_conversions = 0
            st.rerun()

    # Main content area - Fixed two-column layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Input Section
        st.markdown("### 📥 Input Code")
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        
        code_input = st.text_area(
            "Enter your code here",
            value=st.session_state.current_code_input,
            placeholder="Paste your code here or use templates below...",
            height=250,
            label_visibility="collapsed",
            key="code_input_main"
        )
        
        st.session_state.current_code_input = code_input
        
        # Auto-detect and analysis
        if code_input and code_input.strip():
            detected_lang = detect_language(code_input)
            if detected_lang != "unknown":
                st.success(f"**Detected:** {get_language_display(detected_lang)}")
            
            analysis = analyze_code_complexity(code_input)
            cols = st.columns(4)
            metrics = [
                ("Lines", analysis['total_lines']),
                ("Code", analysis['code_lines']),
                ("Comments", analysis['comment_lines']),
                ("Ratio", f"{analysis['comment_ratio']:.1%}")
            ]
            
            for col, (label, value) in zip(cols, metrics):
                with col:
                    st.metric(label, value)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick Templates
        st.markdown("### ⚡ Quick Templates")
        temp_col1, temp_col2, temp_col3 = st.columns(3)
        
        with temp_col1:
            if st.button("🐍 Python", use_container_width=True, key="py_temp"):
                st.session_state.current_code_input = set_code_template("python")
                st.session_state.current_source_lang = "python"
                st.rerun()
                
        with temp_col2:
            if st.button("📜 JavaScript", use_container_width=True, key="js_temp"):
                st.session_state.current_code_input = set_code_template("javascript")
                st.session_state.current_source_lang = "javascript"
                st.rerun()
                
        with temp_col3:
            if st.button("☕ Java", use_container_width=True, key="java_temp"):
                st.session_state.current_code_input = set_code_template("java")
                st.session_state.current_source_lang = "java"
                st.rerun()

    with col2:
        # Settings Section
        st.markdown("### ⚙️ Conversion Settings")
        
        # Language selection with swap
        lang_col1, lang_col2, lang_col3 = st.columns([2, 2, 1])
        
        with lang_col1:
            source_lang = st.selectbox(
                "From Language",
                list(LANGUAGES.keys()),
                format_func=lambda x: get_language_display(x),
                index=list(LANGUAGES.keys()).index(st.session_state.current_source_lang),
                key="source_lang_select"
            )
        
        with lang_col2:
            available_targets = [lang for lang in LANGUAGES.keys() if lang != source_lang]
            current_target_index = 0
            if st.session_state.current_target_lang in available_targets:
                current_target_index = available_targets.index(st.session_state.current_target_lang)
                
            target_lang = st.selectbox(
                "To Language",
                available_targets,
                format_func=lambda x: get_language_display(x),
                index=current_target_index,
                key="target_lang_select"
            )
        
        with lang_col3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄", help="Swap languages"):
                swap_languages()
                st.rerun()
        
        st.session_state.current_source_lang = source_lang
        st.session_state.current_target_lang = target_lang
        
        # Language info
        source_info = get_language_info(source_lang)
        target_info = get_language_info(target_lang)
        
        info_col1, info_col2 = st.columns(2)
        with info_col1:
            st.markdown(f"""
            <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 5px 0;'>
                <strong>{get_language_display(source_lang)}</strong><br>
                • {source_info['paradigm']}<br>
                • {source_info['typing']} typing<br>
                • {source_info['year']}
            </div>
            """, unsafe_allow_html=True)
        
        with info_col2:
            st.markdown(f"""
            <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 5px 0;'>
                <strong>{get_language_display(target_lang)}</strong><br>
                • {target_info['paradigm']}<br>
                • {target_info['typing']} typing<br>
                • {target_info['year']}
            </div>
            """, unsafe_allow_html=True)
        
        # Conversion options
        st.markdown("### 🎯 Conversion Options")
        
        opt_col1, opt_col2 = st.columns(2)
        with opt_col1:
            optimization_level = st.select_slider(
                "Optimization",
                options=["Basic", "Optimized", "Highly Optimized"],
                value="Optimized"
            )
            
        with opt_col2:
            include_comments = st.checkbox("Include Comments", value=True)
            add_error_handling = st.checkbox("Add Error Handling", value=False)

    # Convert Button - Centered
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        convert_clicked = st.button(
            "🚀 CONVERT CODE", 
            use_container_width=True, 
            type="primary",
            key="convert_btn_main"
        )

    # Conversion Logic and Results
    if convert_clicked:
        if code_input and code_input.strip():
            with st.spinner(f"Converting from {get_language_display(source_lang)} to {get_language_display(target_lang)}..."):
                try:
                    # Create prompt template
                    template = PromptTemplate(
                        template=(
                            "Convert the following code from {source_lang} to {target_lang}. "
                            "Optimization level: {optimization_level}. "
                            "{comments_instruction}"
                            "{error_handling_instruction}"
                            "\n\nOriginal code:\n```{source_lang}\n{programme}\n```\n\n"
                            "Converted code:\n"
                        ),
                        input_variables=['programme', 'source_lang', 'target_lang', 'optimization_level', 'comments_instruction', 'error_handling_instruction']
                    )
                    
                    comments_instruction = "Preserve all comments." if include_comments else "Remove all comments."
                    error_handling_instruction = "Add error handling." if add_error_handling else ""
                    
                    chain = template | model | parser
                    result = chain.invoke({
                        'programme': code_input,
                        'source_lang': source_lang,
                        'target_lang': target_lang,
                        'optimization_level': optimization_level,
                        'comments_instruction': comments_instruction,
                        'error_handling_instruction': error_handling_instruction
                    })
                    
                    # Store in history
                    history_item = {
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'input': code_input,
                        'output': result,
                        'from_lang': source_lang,
                        'to_lang': target_lang
                    }
                    
                    st.session_state.conversion_history.append(history_item)
                    st.session_state.total_conversions += 1
                    st.session_state.converted_code = result
                    
                    # Display Results
                    st.markdown("### ✅ Conversion Result")
                    st.markdown('<div class="output-card">', unsafe_allow_html=True)
                    
                    st.code(result, language=target_lang)
                    
                    # Action buttons
                    st.markdown("### 🛠️ Actions")
                    action_col1, action_col2, action_col3 = st.columns(3)
                    
                    with action_col1:
                        if st.button("📋 Copy Code", use_container_width=True):
                            if copy_to_clipboard(result):
                                st.success("Copied to clipboard!")
                    
                    with action_col2:
                        filename = f"converted_code.{target_lang}"
                        st.download_button(
                            "💾 Download",
                            result,
                            file_name=filename,
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    with action_col3:
                        if st.button("🔄 New", use_container_width=True):
                            st.session_state.current_code_input = ""
                            st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Metrics
                    with st.expander("📊 Conversion Metrics"):
                        input_analysis = analyze_code_complexity(code_input)
                        output_analysis = analyze_code_complexity(result)
                        
                        met_col1, met_col2, met_col3, met_col4 = st.columns(4)
                        with met_col1:
                            st.metric("Input Lines", input_analysis['total_lines'])
                        with met_col2:
                            st.metric("Output Lines", output_analysis['total_lines'])
                        with met_col3:
                            st.metric("Input Chars", len(code_input))
                        with met_col4:
                            st.metric("Output Chars", len(result))
                        
                except Exception as e:
                    st.error(f"Conversion failed: {str(e)}")
        else:
            st.warning("Please enter some code to convert.")

    # Features Section - Always visible
    st.markdown("---")
    st.markdown("## ✨ Advanced Features")
    
    feat_col1, feat_col2, feat_col3 = st.columns(3)
    
    with feat_col1:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### 🔍 Code Analysis")
        st.write("Analyze code complexity and structure")
        if st.button("Run Analysis", key="analyze_btn"):
            if code_input:
                analysis = analyze_code_complexity(code_input)
                st.info(f"Analysis: {analysis['code_lines']} code lines, {analysis['comment_lines']} comments")
            else:
                st.warning("Enter code first")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with feat_col2:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### 📚 Batch Processing")
        st.write("Convert multiple files at once")
        uploaded_files = st.file_uploader(
            "Upload files", 
            accept_multiple_files=True, 
            label_visibility="collapsed",
            key="file_upload"
        )
        if uploaded_files:
            st.success(f"{len(uploaded_files)} files ready")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with feat_col3:
        st.markdown('<div class="feature-card">', unsafe_allow_html=True)
        st.markdown("### 🎯 Code Optimization")
        st.write("Get optimized versions of your code")
        if st.button("Optimize", key="optimize_btn"):
            st.info("Optimization feature coming soon!")
        st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; padding: 20px;'>"
        "🚀 <strong>Code Converter Pro</strong> • Powered by AI • Built with Streamlit"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()