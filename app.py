import streamlit as st
import pickle
import numpy as np
import os
import requests

# Function to download books.pkl from GitHub Release
def download_books_pkl():
    pkl_path = 'books.pkl'
    if not os.path.exists(pkl_path):
        st.info("📥 Downloading books.pkl from GitHub Release...")
        try:
            url = "https://github.com/himanshuarya993/Book_Recommendation_System/releases/download/v1.0/books.pkl"
            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                with open(pkl_path, 'wb') as f:
                    f.write(response.content)
                st.success("✅ Downloaded books.pkl successfully!")
                return True
            else:
                st.error(f"Failed to download books.pkl (Status: {response.status_code})")
                return False
        except Exception as e:
            st.error(f"Download error: {e}")
            return False
    return True

# ---- Load data with proper Windows paths ----
try:
    if not download_books_pkl():
        st.stop()
    
    popular_df = pickle.load(open('popular.pkl', 'rb'))
    pt = pickle.load(open('pt.pkl', 'rb'))
    books = pickle.load(open('books.pkl', 'rb'))
    similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))
except Exception as e:
    st.error(f"Error loading files: {e}")
    st.stop()  # stop execution if files not loaded

# ---- Streamlit Page Configuration ----
st.set_page_config(page_title="Book Recommender", layout="wide")
st.title("📚 Book Recommender System")

# ---- Sidebar Menu ----
menu = st.sidebar.selectbox("Menu", ["Home", "Recommend Books"])

# ---- HOME PAGE ----
if menu == "Home":
    st.header("Top 50 Books")
    
    # Display top 50 books
    for i in range(min(50, len(popular_df))):
        cols = st.columns([1, 2, 1, 1])  # adjust column width ratios
        with cols[0]:
            st.image(popular_df["Image-URL-M"].iloc[i], width=100)
        with cols[1]:
            st.write("**Book:**", popular_df["Book-Title"].iloc[i])
            st.write("**Author:**", popular_df["Book-Author"].iloc[i])
        with cols[2]:
            st.write("**Votes:**", popular_df["num_ratings"].iloc[i])
        with cols[3]:
            st.write("**Rating:**", popular_df["avg_rating"].iloc[i])

# ---- RECOMMENDATION PAGE ----
if menu == "Recommend Books":
    st.header("🔍 Find Similar Books")
    
    user_input = st.text_input("Enter Book Name")

    if st.button("Recommend"):
        try:
            # Find the book index in pivot table
            index = np.where(pt.index == user_input)[0][0]
            
            # Get top 4 similar books
            similar_items = sorted(
                list(enumerate(similarity_scores[index])),
                key=lambda x: x[1],
                reverse=True
            )[1:5]  # skip the book itself
            
            st.subheader("Recommended Books:")
            
            for i in similar_items:
                temp_df = books[books['Book-Title'] == pt.index[i[0]]].drop_duplicates('Book-Title')
                
                title = temp_df['Book-Title'].values[0]
                author = temp_df['Book-Author'].values[0]
                img = temp_df['Image-URL-M'].values[0]
                
                cols = st.columns([1, 2])
                with cols[0]:
                    st.image(img, width=120)
                with cols[1]:
                    st.write(f"**{title}**")
                    st.write(f"*{author}*")
                    
        except IndexError:
            st.error("Book not found! Make sure the spelling matches your dataset.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
