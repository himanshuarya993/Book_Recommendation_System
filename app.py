import streamlit as st
import pickle
import numpy as np

# Set page config
st.set_page_config(
    page_title="Book Recommendation System",
    page_icon="📚",
    layout="wide"
)

# Load pickle files
try:
    popular_df = pickle.load(open(r'D:\Book_Recommendation_System\popular.pkl', 'rb'))
    pt = pickle.load(open(r'D:\Book_Recommendation_System\pt.pkl', 'rb'))
    books = pickle.load(open(r'D:\Book_Recommendation_System\books.pkl', 'rb'))
    similarity_scores = pickle.load(open(r'D:\Book_Recommendation_System\similarity_scores.pkl', 'rb'))
except Exception as e:
    st.error(f"Error loading files: {e}")
    st.stop()

# Recommendation function
def recommend(book_name):
    try:
        index = np.where(pt.index == book_name)[0][0]
        similar_items = sorted(list(enumerate(similarity_scores[index])), 
                              key=lambda x: x[1], reverse=True)[1:5]
        
        data = []
        for i in similar_items:
            item = []
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
            data.append(item)
        
        return data
    except Exception as e:
        st.error(f"Error generating recommendations: {e}")
        return []

# Main app
st.title("📚 Book Recommendation System")

# Create tabs
tab1, tab2 = st.tabs(["Popular Books", "Recommend for You"])

# Tab 1: Popular Books
with tab1:
    st.header("Top 50 Popular Books")
    
    cols = st.columns(4)
    for idx, row in popular_df.iterrows():
        col = cols[idx % 4]
        with col:
            st.image(row['Image-URL-M'], width=120)
            st.write(f"**{row['Book-Title']}**")
            st.caption(f"Author: {row['Book-Author']}")
            st.caption(f"⭐ {row['avg_rating']:.2f} | 📊 {int(row['num_ratings'])} ratings")

# Tab 2: Recommendations
with tab2:
    st.header("Get Personalized Recommendations")
    
    book_list = pt.index.tolist()
    selected_book = st.selectbox("Select a book:", book_list)
    
    if st.button("Recommend Similar Books"):
        recommended_books = recommend(selected_book)
        
        if recommended_books:
            cols = st.columns(2)
            for idx, book_data in enumerate(recommended_books):
                col = cols[idx % 2]
                with col:
                    st.image(book_data[2], width=150)
                    st.write(f"**{book_data[0]}**")
                    st.caption(f"Author: {book_data[1]}")
        else:
            st.warning("Could not generate recommendations for this book.")
