library(readxl)
library(ranger)
library(rpart)
library(xgboost)
library(vip)
library(ggplot2)

#cta1 <- plsr(LAA_thrombus ~ Sex + Age + AF + CHF + vascular_disease + Diabetes + Hypertension + pre_mRS + chads_vasc + RR_sys + RR_dia + HR + NIHSS_0 + DLP + LA_vol + EDD + ESD + EF + Ao_insuff + Pulm_insuff + Mitr_insuff + Tricusp_insuff, ncomp = 10, data = ctaTrain, validation = "LOO")

Stroke_CTA_filtered_v3$Sex <- as.factor(Stroke_CTA_filtered_v3$Sex)
Stroke_CTA_filtered_v3$AF <- as.factor(Stroke_CTA_filtered_v3$AF)
Stroke_CTA_filtered_v3$LAA_thrombus <- as.factor(Stroke_CTA_filtered_v3$LAA_thrombus)
Stroke_CTA_filtered_v3$LAA_morphology <- as.factor(Stroke_CTA_filtered_v3$LAA_morphology)

Stroke_CTA_filtered_v3$Ao_insuff <- as.factor(Stroke_CTA_filtered_v3$Ao_insuff)
Stroke_CTA_filtered_v3$Pulm_insuff <- as.factor(Stroke_CTA_filtered_v3$Pulm_insuff)
Stroke_CTA_filtered_v3$Mitr_insuff <- as.factor(Stroke_CTA_filtered_v3$Mitr_insuff)
Stroke_CTA_filtered_v3$Tricusp_insuff <- as.factor(Stroke_CTA_filtered_v3$Tricusp_insuff)


tree <- rpart(LAA_thrombus ~ ., data = Stroke_CTA_filtered_v2)

rfo <- ranger(LAA_thrombus ~ ., data = Stroke_CTA_filtered_v2, importance = "impurity")

bst <- xgboost(
       data = data.matrix(subset(Stroke_CTA_filtered_v3, select = c(Sex, Age, AF, chads_vasc, RR_sys, RR_dia, NIHSS_0, CRP_first, TropT, proBNP, WBC, INR, APTI, HgbA1c_percent, HgbA1c_mmol, Triglicerid, LDL_chol, D_dimer, LAA_morphology, LA_vol, EDD, ESD, EDV, ESV, EF, IVS, PW, TAPSE, EA_ratio, Ao_insuff, Pulm_insuff, Mitr_insuff, Tricusp_insuff))),
       label = Stroke_CTA_filtered_v3$LAA_thrombus, 
       objective = "reg:linear",
       nrounds = 100, 
       max_depth = 5, 
       eta = 0.3,
       verbose = 0  # suppress printing
       )
vi_tree <- tree$variable.importance
vi_rfo <- rfo$variable.importance
vi_bst <- xgb.importance(model = bst)

barplot(vi_tree, horiz = TRUE, las = 1)
barplot(vi_rfo, horiz = TRUE, las = 1)
xgb.ggplot.importance(vi_bst, palette="Spectral")


p1 <- vip(tree)
p2 <- vip(rfo, width = 0.5, aesthetics = list(fill = "green3"))
vip(bst) + labs(x="Features", y="Importance")
grid.arrange(p1, p3, ncol = 2)
