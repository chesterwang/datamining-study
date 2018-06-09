
# 
train_data_df <- read.csv(
  "/home/chester/Downloads/training.txt",
  sep = "\t",
  header = FALSE,
  quote = "",
  stringsAsFactor=F,
  col.names = c("sentiment","text")
);
test_data_df <- read.csv(
  "/home/chester/Downloads/testdata.txt",
  sep = "\t",
  header = FALSE,
  quote = "",
  stringsAsFactor=F,
  col.names = "text"
);
train_data_df$sentiment <- as.factor(train_data_df$sentiment);
table(train_data_df$sentiment);

mean(sapply(sapply(train_data_df$text, strsplit, " "), length));

library(tm);

corpus <- Corpus(VectorSource(c(train_data_df$text, test_data_df$text)))
corpus <- tm_map(corpus, content_transformer(tolower))
corpus <- tm_map(corpus, content_transformer(removePunctuation))
# cannot use the following code
#reason and solutions: http://stackoverflow.com/questions/24771165/r-project-no-applicable-method-for-meta-applied-to-an-object-of-class-charact
#corpus <- tm_map(corpus, content_transformer(removeWords, stopwords("english")))
#corpus <- tm_map(corpus, content_transformer(stripWhitespace))
#corpus <- tm_map(corpus, content_transformer(stemDocument))

dtm <- DocumentTermMatrix(corpus)
sparse <- removeSparseTerms(dtm, 0.99)

important_words_df <- as.data.frame(as.matrix(sparse))
#make.names Make syntactically valid names out of character vectors.
colnames(important_words_df) <- make.names(colnames(important_words_df))
# split into train and test
important_words_train_df <- head(important_words_df, nrow(train_data_df))
important_words_test_df <- tail(important_words_df, nrow(test_data_df))

# Add to original dataframes
train_data_words_df <- cbind(train_data_df, important_words_train_df)
test_data_words_df <- cbind(test_data_df, important_words_test_df)

# Get rid of the original Text field
train_data_words_df$text <- NULL
test_data_words_df$text <- NULL

library(caTools)
set.seed(1234)
spl <- sample.split(train_data_words_df$sentiment, .85)
eval_train_data_df <- train_data_words_df[spl==T,]
eval_test_data_df <- train_data_words_df[spl==F,]
log_model <- glm(sentiment~., data=eval_train_data_df, family=binomial)
log_pred <- predict(log_model, newdata=eval_test_data_df, type="response")
table(eval_test_data_df$sentiment, log_pred>.5)

log_pred_test <- predict(log_model, newdata=test_data_words_df, type="response")
test_data_df$sentiment <- log_pred_test>.5