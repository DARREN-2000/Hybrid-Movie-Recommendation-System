


# Movie Recommendation System Using Hybrid Filtering

## Overview
This project implements a movie recommendation system that uses hybrid filtering techniques to provide personalized movie recommendations to users. By combining content-based filtering (based on movie features) and collaborative filtering (based on user preferences), this system aims to overcome the limitations of individual approaches such as the cold start problem, sparsity, and scalability issues.

## Background
The exponential growth of data on the World Wide Web makes it difficult for users to find relevant content. Recommendation systems help filter valuable information from vast amounts of data. This movie recommendation system specifically provides personalized recommendations based on user preferences and behaviors.

## Key Features
- **Hybrid Filtering Approach**: Combines content-based and collaborative filtering techniques
- **Personalized Recommendations**: Tailored suggestions based on user preferences
- **Custom Dataset**: Uses IMDB dataset verified by Wikipedia, avoiding biases present in commonly used datasets like MovieLens
- **Age and Genre Segregation**: Allows for more personalized recommendations based on demographic factors

## Methodology
The system employs three main filtering approaches:

1. **Collaborative Filtering**: Predicts and recommends items based on similar users' preferences
2. **Content-Based Filtering**: Provides recommendations based on similar types of user input
3. **Hybrid Approach**: Combines both methods to overcome individual disadvantages

## Dataset
Unlike many recommendation systems that rely on the MovieLens dataset (which has reliability issues with rating information and is biased toward highly-rated movies), this project uses:
- IMDB dataset
- Further verified by Wikipedia
- Supports segregation based on age and different genres

## Technologies Used
- Python
- Data analysis libraries (Pandas, NumPy)
- Machine learning frameworks
- Data visualization tools

## Installation
```bash
# Clone the repository
git clone https://github.com/DARREN-2000/movie-recommendation-system.git

# Navigate to the project directory
cd movie-recommendation-system

# Install required dependencies
pip install -r requirements.txt
```

## Usage
```python
# Import the recommendation engine
from recommender import MovieRecommender

# Initialize the recommender
recommender = MovieRecommender()

# Train the model
recommender.train()

# Get movie recommendations for a user
recommendations = recommender.get_recommendations(user_id=123)
```

## Conference Paper Article About My Project

(https://www.researchgate.net/publication/389884094_Movie_Recommendation_System_using_Hybrid_filtering)

## Author
MORRIS DARREN BABU  
M.S. Data Science  
B.E. Computer Science  
Department of Computer Science  
Friedrich-Alexander-University Erlangen-Nürnberg, Germany

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- IMDB and Wikipedia for the dataset resources
