import streamlit as st
import pickle
import numpy as np

# ---- Load data with proper Windows paths ----
try:
    popular_df = pickle.load(open(r'D:\Book_Recommendation_System\popular.pkl', 'rb'))
    pt = pickle.load(open(r'D:\Book_Recommendation_System\pt.pkl', 'rb'))
    books = pickle.load(open(r'D:\Book_Recommendation_System\books.pkl', 'rb'))
    similarity_scores = pickle.load(open(r'D:\Book_Recommendation_System\similarity_scores.pkl', 'rb'))
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
    
    from fuzzywuzzy import process
    
    user_input = st.text_input("Enter Book Name")

    if st.button("Recommend"):
        try:
            # Use fuzzy matching to find similar book titles
            available_books = pt.index.tolist()
            best_match = process.extractOne(user_input, available_books)
            
            if best_match and best_match[1] >= 60:  # 60% match threshold
                matched_book = best_match[0]
                st.info(f"📖 Searching for books similar to: **{matched_book}**")
                
                # Find the book index in pivot table
                index = np.where(pt.index == matched_book)[0][0]
                
                # Get top 4 similar books
                similar_items = sorted(
                    list(enumerate(similarity_scores[index])),
                    key=lambda x: x[1],
                    reverse=True
                )[1:5]  # skip the book itself
                
                st.subheader("📚 Recommended Books:")
                
                for i in similar_items:
                    temp_df = books[books['Book-Title'] == pt.index[i[0]]].drop_duplicates('Book-Title')
                    
                    if len(temp_df) > 0:
                        title = temp_df['Book-Title'].values[0]
                        author = temp_df['Book-Author'].values[0]
                        img = temp_df['Image-URL-M'].values[0]
                        
                        cols = st.columns([1, 2])
                        with cols[0]:
                            st.image(img, width=120)
                        with cols[1]:
                            st.write(f"**{title}**")
                            st.write(f"*{author}*")
            else:
                st.warning(f"❌ No similar book found for '{user_input}'. Try a different spelling or book name!")
                
                # Suggest closest matches
                close_matches = process.extract(user_input, available_books, limit=5)
                if close_matches:
                    st.info("Did you mean one of these?")
                    for match, score in close_matches:
                        st.write(f"• {match} ({score}% match)")
                    
        except Exception as e:
            st.error(f"An error occurred: {e}")
