#https://www.kaggle.com/benhamner/digit-recognizer/random-forest-benchmark/code

library(randomForest)
set.seed(0)

numTrain <- 10000
numTrees <- 25

train <- read.csv("/home/chester/gitlab.wangtongpeng.com/chester-dm/MNIST/data/train.csv")
test <- read.csv("/home/chester/gitlab.wangtongpeng.com/chester-dm/MNIST/data/test.csv")

rows <- sample(1:nrow(train), numTrain)
labels <- as.factor(train[rows,1])
train <- train[rows,-1]

rf <- randomForest(train, labels, xtest=test, ntree=numTrees)
predictions <- data.frame(ImageId=1:nrow(test), Label=levels(labels)[rf$test$predicted])

head(predictions)
write.csv(predictions, "/home/chester/gitlab.wangtongpeng.com/chester-dm/MNIST/data/rf_benchmark.csv",quote=FALSE,row.names = FALSE)


