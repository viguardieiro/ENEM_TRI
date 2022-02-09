library(ltm)
library(CTT)
library(Metrics)

print("[INFO] Processando dados do ENEM 2019...")

mean_2009 <- 0.0616810996437219
sd_2009 <- 0.885383569242728

print(paste0("[INFO] Começando análise das questões de alta renda"))
print("[INFO] Lendo gabaritos dos alunos concluintes...")

ch <- read.csv(file='../Data/Processed/ENEM2019/CR_data/CR_alta_renda_ing.csv')
ch.itens <- ch[,3:length(ch)]
ch.true_scores <- ch[,2]

print("[INFO] Gabaritos lidos.")
print(paste0("[INFO] Total de participantes: ", nrow(ch)))

print("[INFO] Checando se os parâmetros já foram calculados...")
file_name = "../Data/Processed/ENEM2019/Parameters/Parametros_CR_alta_renda_ing.csv"
if(file.exists(file_name)){
  print("[INFO] Arquivo de parâmetros encontrado.")
  ch.fit <- data.matrix(read.csv(file_name, row.names = 1))
  ch.fit_m <- readRDS(file="../Data/Processed/ENEM2019/Parameters/Fit_CR_alta_renda_ing.RData")
} else{
  print("[INFO] Arquivo de parâmetros não encontrado.")
  print("[INFO] Calculando parâmetros...")
  #ch.fit <- est(ch.itens, model = "3PL", engine = "ltm")$est
  ch.fit_m <- tpm(ch.itens, control=list(GHk=40, method="L-BFGS-B"))
  print(ch.fit_m)
  saveRDS(ch.fit_m,file="../Data/Processed/ENEM2019/Parameters/Fit_CR_alta_renda_ing.RData")
  ch.fit <- coef(ch.fit_m)
  print("[INFO] Parâmetros calculados.")
  print("[INFO] Salvando parâmetros...")
  write.csv(ch.fit, file_name)
  print("[INFO] Parâmetros salvos.")
}

print("[INFO] Parâmetros encontrados:")
print(ch.fit)
print("")

print("[INFO] Checando se as notas já foram estimadas...")
file_name = "../Data/Processed/ENEM2019/Estimated Scores/CR_alta_renda_ing.csv"
if(file.exists(file_name)){
  print("[INFO] Arquivo de notas encontrado.")
  ch.score <- data.matrix(read.csv(file_name, row.names = 1))
  ch.scoret <- data.matrix(read.csv("../Data/Processed/ENEM2019/Estimated Scores/CR_alta_renda_ing_0_1000.csv", row.names = 1))
} else{
  print("[INFO] Arquivo de notas não encontrado.")
  print("[INFO] Calculando notas...")
  #ch.score <- eap(ch.itens,ch.fit, qu=normal.qu())
  ch.score <- factor.scores(ch.fit_m, resp.patterns=ch.itens, method="EAP")$score[,"z1"]
  ch.scoret <- ch.score*(100/sd_2009) + 500 - 100*mean_2009/sd_2009

  print("[INFO] Notas dos concluintes estimadas.")
  print("[INFO] Salvando notas dos concluintes...")
  write.csv(ch.score, file_name)
  write.csv(ch.scoret, "../Data/Processed/ENEM2019/Estimated Scores/CR_alta_renda_ing_0_1000.csv")
  print("[INFO] Notas dos concluintes salvas.")
}

print(paste0("[INFO] Nota média: ", mean(ch.score)))
print(paste0("[INFO] Desvio padrão: ", sd(ch.score)))

png(file="../Images/Histogram-CR_alta_renda_ing2019.png")
hist(ch.scoret, main="Histogram of Scores - High Income", col=rgb(1,0,0,1/4), xlab="Score", breaks=15,
     ylim=c(0,500000), xlim=c(0,1000))
hist(ch.true_scores, xlab="True Score",  breaks=15, col=rgb(0,0,1,1/4), add=T)
legend("topright",legend=c("True Score", "Estimated Score"), fill = c(rgb(0,0,1,1/4), rgb(1,0,0,1/4)), 
       border = "black")
#close("../Images/Histogram-CR_baixa_renda_ing2019.png")
#---------------------------------------------------------

png(file="../Images/Errors-CR_alta_renda_ing2019.png")
plot(ch.true_scores, ch.scoret, cex = .1,
    xlab="True Score", ylab="Estimated Score",
    xlim=c(0,200), ylim=c(0,200)) 
abline(a=0, b=1)
#close("../Images/Errors-CR_baixa_renda_ing2019.png")
#---------------------------------------------------------
png(file="../Images/Hist_Errors-CR_alta_renda_ing2019.png")
hist(ch.scoret-ch.true_scores, main="Histogram of Errors - High Income", col=rgb(1,0,0,1/4), 
    xlab="Error", breaks=15, ylim=c(0,200000), xlim=c(-1000,1000))
#close("../Images/Hist_Errors-CR_baixa_renda_ing2019.png")

print(paste0("[INFO] Erro de estimação (RMSE): ", rmse(ch.true_scores, ch.scoret)))
print("-----------------------------------------")