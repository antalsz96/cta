library(readxl)
library(mixOmics)
library(dplyr)
library(mdatools)
library(reshape2)

setwd("~/Desktop/PhD/Projects/Stroke_CTA")
stroke_df <- read_excel("stroke_clean_nums.xlsx")
#stroke_history_df <- read_excel("stroke_history.xlsx")

factor_list = list("Sex", "chads_stroke", "AF", "pangásos_SZE", "vascular_disease", "Diabetes", "Hypertension", "Alcohol", "Smoking", "Anticoag_prev", "TAG_prev", "DM_ther", "LAA_thrombus")
for (i in colnames(stroke_df)){
        if (i %in% factor_list){
                stroke_df[[i]] <- as.factor(stroke_df[[i]])
                print(class(stroke_df[[i]]))
                
        }
}

col_means <- stroke_df %>% summarise_if(is.numeric, mean)
col_sd <- stroke_df %>% summarise_if(is.numeric, sd)

evz <- stroke_df
dvz <- data.frame(stroke_df[["LAA_thrombus"]])

for(i in 1:ncol(col_means)) {       # for-loop over columns
        evz[ , i] <- (stroke_df[ , i] - col_means[[i]])/col_sd[[i]]
        
}

for(i in 1:nrow(dvz)) {       # for-loop over rows
        dvz[i, ] <- (dvz[i, ] - col_means[["LAA_thrombus"]]/col_sd[["LAA_thrombus"]])
}

x <- data.matrix(evz[-13])
y <- evz[["LAA_thrombus"]]

# x_noz <- data.matrix(stroke_df[-13])
# y_noz <- stroke_df$LAA_thrombus

MyResult.plsda <- plsda(x,y)
plotIndiv(MyResult.plsda)
plotVar(MyResult.plsda)
plotLoadings(MyResult.plsda, contrib = 'max', method = 'mean', comp = 1, legend = FALSE, col.ties = "white")

y <- as.factor(y)
mda_pls <- mdatools::plsda(x,y)
plotVIPScores(mda_pls, type = "h", show.labels=TRUE, legend=FALSE, ncomp = 2, set_title="Predictors for LAA thrombus")

# mda_pls_noz <- mdatools::plsda(x_noz,y_noz)
# plotVIPScores(mda_pls_noz, type = "h", show.labels=TRUE, legend=FALSE)


vip_scores <- vipscores(mda_pls)
vip_scores.T <- melt(vip_scores)

ggplot(data=long, aes(x=Var1, y=value)) + 
        geom_col() + 
        scale_y_continuous(limits=c(0, max(long$value)))
