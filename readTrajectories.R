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
    allTrajectories<-sapply(allLevels, readTrajectories)
    remove(allLevels)
    c<-read.table(str_join(subject,"/condition.txt"))
    colnames(c)<-"Condition"
    medianDevs<-vector()
    for (i in 1:length(allTrajectories)){
        dev<-getDev(allTrajectories[[i]])
        medianDevs[i]<-dev
    }
    #this is the mean of the median of absolute deviations per trial, taken by level.  So, this will indicate if the absoulte devs
    #are becoming smaller as the levels increase
    groupByLevel<-split(medianDevs,as.numeric(gl(length(medianDevs),16,length(medianDevs)))) 
    meanOfDevsByLevel<-sapply(groupByLevel, mean)
    remove(allTrajectories)
    meanOfDevsByLevel<-cbind(meanOfDevsByLevel, c)
    meanOfDevsByLevel
}

readEverything<-function(){
    #this does all the work, will take a while to run depending on the number of subject folders
    png("deviationsPlot.png", width = 860, height = 548)
    dirs<-list.dirs(recursive = FALSE)
    dirs_of_interest<-dirs[grepl("Subject", dirs)]
    allSubjectMeans<-list()
    for (subj in dirs_of_interest){
        subjData<-readSubject(subj)
        allSubjectMeans[[subj]]<-subjData
    }
    print(allSubjectMeans)
    cond1Means<-NULL
    cond2Means<-NULL
    for (subject in allSubjectMeans){
        if (subject$Condition==1){
            cond1Means<-rbind(cond1Means,subject$meanOfDevsByLevel)
        }
        else if (subject$Condition==2){
            cond2Means<-rbind(cond2Means,subject$meanOfDevsByLevel)
        }
    }
    cond1<-apply(cond1Means, 2, mean)
    cond2<-apply(cond2Means, 2, mean)
    plot(1:length(cond1), cond1, pch=19, col="red", xlab = "Level", ylab="Mean of Median Abs. Deviations (pixels)", main = "Mean of Median Absolute Deviations from Enemies by Level", ylim = c(0,400))
    points(1:length(cond2), cond2, pch=19, col="blue")
    legend("bottomright", c("Condition 1", "Condition2"), pch=19, col= c('red', 'blue'))
    dev.off();
    list(cond1,cond2)
}