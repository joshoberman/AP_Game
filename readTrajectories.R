#These functions work to read and summarize the absolute deviations of the player from the range of where they can shoot the enemy.
#This measurement serves as an indication of category learning--if absolute deviations decrease per level, the player is likely
#anticipating where the enemy will come from based on the auditory cue.

#The only function that needs to be run is readEverything(), with no arguments.  Make sure your working directory
#is set to where all the subjects folders are located

readTrajectories<-function(trajectory_files){
    #read in the .txt files to data frame, append data frame to "trajects list"
    trajects<-list()
    for (file in trajectory_files){
        traject<-read.table(file, sep=",",col.names=c("Positon", "Time", "Enemy Type"))
        traject<-as.data.frame(traject)
        trajects[[file]]<-traject
    }
    trajects 
}

getDev<-function(trajectories){
    #this function is applied to each file i.e. each trial, it returns the median of the absolute deviations from the enemy
    ##for that trial
    getAbsDev<-function(point, enemy_type){
        target_range<-NULL
        if (enemy_type=="A"){
            target_range<-10:42
        }
        else if (enemy_type=="B"){
            target_range<-333:365
        }
        else if (enemy_type=="C"){
            target_range<-666:698
        }
        else if (enemy_type=="D"){
            target_range<-958:990
        }
        if(point %in% target_range){
            absDev<-0   
        }
        else{
            absDev<-abs(point-median(target_range))
        }
        absDev
    }
    absDevs<-NULL
    i = 1
    for (i in 1:nrow(trajectories)){
        absDevs<-c(absDevs,getAbsDev(point = trajectories$Positon[i], enemy_type = trajectories$Enemy.Type[i]))
    }
    #we're taking the median because it is less sensitive to the skewness that will be introduced because of different positions
    #of the player when the auditory cue starts
    medianOfDevs<-median(absDevs)
    medianOfDevs
}

readSubject<-function(subject){
    ##this function is used to read in a given subject's data by level
    library(stringr)
    dirs<-list.dirs(subject, full.names = TRUE)
    dirs_of_interest<-dirs[grepl("Level",dirs)]
    allLevels<-lapply(dirs_of_interest, list.files, full.names = TRUE)
    allLevels<-unlist(allLevels)
    #we need to order by trial number! fancy reg exp should help!
    properOrder<-gsub(".*Subject+\\s+\\d+\\d+/Level+\\s+\\d+/?", "", allLevels)
    properOrder<-gsub(".txt", "", properOrder)
    properOrder<-as.numeric(properOrder)
    toSort<-data.frame(allLevels,properOrder)
    sorted<-toSort[with(toSort, order(properOrder, allLevels)), ]
    #read the sorted trajectories
    allTrajectories<-sapply(sorted$allLevels, readTrajectories)
    remove(sorted)
    #add condition and subject columns
    c<-read.table(str_join(subject,"/condition.txt"))
    colnames(c)<-"Condition"
    Subject<-gsub("^.*Subject+\\s", "", subject)
    Subject<-as.integer(Subject)
    #get the deviations for the trajectories
    medianDevs<-vector()
    for (i in 1:length(allTrajectories)){
        dev<-getDev(allTrajectories[[i]])
        medianDevs[i]<-dev
    }
    #this is the mean of the median of absolute deviations per trial, taken by level.  So, this will indicate if the absoulte devs
    #are becoming smaller as the levels increase
    #split the data by levels w/ the 16 trials per level
    groupByLevel<-split(medianDevs,as.numeric(gl(length(medianDevs),16,length(medianDevs)))) 
    meanOfDevsByLevel<-sapply(groupByLevel, mean)
    remove(allTrajectories)
    levels<-1:12
    for(i in levels){
        levels[i] = str_join("MADLevel",i)
    }
    meanMADs<-data.frame()
    meanMADs<-rbind(meanMADs, meanOfDevsByLevel)
    colnames(meanMADs)<-levels
    meanMADs<-cbind(Subject, c, meanMADs)
    meanMADs
}

readEverything<-function(){
    #this does all the work, will take a while to run depending on the number of subject folders
    library(ggplot2)
    library(dplyr)
    png("deviationsPlot.png", width = 860, height = 548)
    dirs<-list.dirs(recursive = FALSE)
    dirs_of_interest<-dirs[grepl("Subject", dirs)]
    allSubjectMeans<-list()
    for (subj in dirs_of_interest){
        subjData<-readSubject(subj)
        allSubjectMeans[[subj]]<-subjData
    }
    allSubjectMeans<<-allSubjectMeans
    #get a dataframe with all Subjects
    trajectData<-do.call("rbind", allSubjectMeans)
    trajectData.tbl<-tbl_df(trajectData)
    summaryByLevel<-trajectData.tbl%>%
        group_by(Condition)%>%
        summarise_each(funs(mean), -Subject)
    summaryBySubject<-trajectData.tbl%>%
        group_by(Condition, Subject)%>%
        summarize(meanMAD = mean(MADLevel1:MADLevel12))
    summaryNoGrouping<-trajectData.tbl%>%
        select(-Subject, -Condition)%>%
        summarise_each(funs(mean))
    #the following lets us make a histogram to compare the distro of 2 conditions
    qplot(summaryBySubject$meanMAD, fill = factor(summaryBySubject$Condition), xlab = "Mean MAD (px)")
    ggsave(filename= "MADs_hist.png")
    #construct 3 linear models, 1 for the no-grouping data, and 2 for each condition.
    levelSeries<-as.vector(1:12)
    modelBoth<-lm(unlist(summaryNoGrouping) ~ levelSeries)
    modelCond1<-lm(unlist(summaryByLevel[1, 2:13])~levelSeries)
    modelCond2<-lm(unlist(summaryByLevel[2,2:13])~levelSeries)
    a<-predict(modelCond1, interval = "confidence")
    b<-predict(modelCond2, interval = "confidence")
    #qplot(cond1Means[,1], main = "Mean of MADs by Level Condition 1")
    #ggsave(filename = "Cond1Hist.png")
    #qplot(cond2Means[,1], main = "Mean of MADs by Level Condition2")
    #ggsave(filename = "Cond2Hist.png")
    png("deviationsPlot.png", width = 860, height = 548)
    plot(1:12, unlist(summaryByLevel[1,2:13]), pch=19, col="red", xlab = "Level", ylab="Mean of Median Abs. Deviations (pixels)", main = "Mean of Median Absolute Deviations from Enemies by Level", ylim = c(100,250))
    points(1:12, unlist(summaryByLevel[2,2:13]), pch=19, col="blue")
    legend("bottomleft", c("Condition 1", "Condition2"), pch=19, col= c('red', 'blue'))
    lines(a[,2],lty=2)
    lines(a[,3], lty = 2)
    lines(b[,2], lty = 2)
    lines(b[,3], lty = 2)
    dev.off();
    list(trajectData,modelCond1,modelCond2,modelBoth)
}