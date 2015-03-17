##These functions are used to read the score as it changes over level for each subject
##One only needs to run readAll(), if you want to exclude subjects do so in the code below

readCondition<-function(subject){
    scores<-read.table(str_join(subject, "/scores.txt"))
    ##this function is used to read in the scores list, and get the actual score by level (the actual score is not registered by
    #the game code, just the running tally). So, this code reads in the score tally at i and subtracts it from the tally
    #at i-1
    getScore<-function(scoreList){
        i=2
        newScores=vector(mode="numeric",length=12)
        newScores[1]=scoreList[1]
        while(i<13){
            newScores[i]=scoreList[i]-scoreList[i-1]
            i=i+1
        }
        newScores
    }
    s<-sapply(scores, getScore,simplify=TRUE)
    colnames(s)<-subject
    levels<-1:12
    for(i in levels){
        levels[i] = str_join("Level",i)
    }
    row.names(s)<-levels
    c<-read.table(str_join(subject,"/condition.txt"))
    colnames(c)<-subject
    row.names(c)<-"Condition"
    all<-rbind(c,s)
    #this gives us a nice data frame with scores, level, and condition for the subject
    t(all)
}

readAll<-function(numberSubjects){
    #This function reads in all subject folders scores, groups by condition, and provides a summary graph
    library(dplyr)
    conditions<-NULL
    library(stringr)
    dirs<-list.dirs()
    subjects = 1:numberSubjects
    for (i in subjects){
        subjects[i] = str_join("Subject ", i)
    }
    # here is where u can exclude certain subjects from the analysis
    subjects<-subjects[!((subjects=="Subject 1") | (subjects=="Subject 2") | (subjects == "Subject 23"))]
    allData<-NULL
    i=1
    for (i in 1:length(subjects)){
        allData<-rbind(allData,readCondition(subjects[i]))
    }
    Subject<-row.names(allData)
    allData<-cbind(Subject,allData)
    allData<-as.data.frame(allData, stringsAsFactors = FALSE)
    allData[,3:length(allData)]<-as.numeric(unlist(allData[,3:length(allData)]))
    allData.table<-tbl_df(allData)
    #here we take the mean of the scores across subjects by level for both conditions
    summary<-allData.table%>%
        group_by(Condition)%>%
            summarise_each(funs(mean))
    levels<-as.matrix(summary[,3:length(summary)])
    plot(levels[1,], col="red", main="Mean Score vs. Level", xlab="Level", ylab="Score", type='p', pch=19, ylim=c(20,160))
    points(levels[2,],col="blue",pch=19)
    legend("bottomleft", col = c("red","blue"), legend=c("Condition 1","Condition2"), bty = 1, pch = 19)
    list(allData.table, summary)
}