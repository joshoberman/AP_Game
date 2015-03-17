read_scores<-function(){
    dirs<-list.dirs()
    dirs_of_interest<-dirs[!grepl("Level", dirs)]
    files<-sapply(dirs_of_interest,list.files,full.names=TRUE)
    scores<-lapply(files,function(x){x[grep("scores.txt",x)]})
    scores<-scores[-1]
    scores<-scores[-1]
    scores<-scores[-11]
    s<-sapply(scores,read.table)
    getScore<-function(scoreList){
        i=2
        newScores=vector(mode="numeric",length=12)
        while(i<13){
            newScores[i]=scoreList[i]-scoreList[i-1]
            i=i+1
        }
        newScores
    }
    s<-sapply(s, getScore)
    par(mfrow=c(2,4))
    for (i in 1:8){
        barplot(s[,i])
    }
    
}