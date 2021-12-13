library(ltm)
library(CTT)
library(Metrics)
require(irtoys)

print("[INFO] Processando dados do ENEM 2009...")
print("")

print("[INFO] Começando análise das questões de Ciências Humanas (CH)...")
print("[INFO] Lendo gabaritos dos alunos concluintes do ensino regular...")

ch <- read.csv(file='../Data/Processed/ENEM2009/Concluintes_CH.csv')
ch.itens <- ch[,2:46]
ch.true_scores <- ch[,1]

print("[INFO] Gabaritos lidos.")
print(paste0("[INFO] Total de participantes: ", nrow(ch)))

print("[INFO] Checando se os parâmetros já foram calculados...")
file_name = "../Data/Processed/ENEM2009/Parameters/Parametros_CH_Concluintes.csv"
if(file.exists(file_name)){
  print("[INFO] Arquivo de parâmetros encontrado.")
  ch.fit <- data.matrix(read.csv(file_name, row.names = 1))
} else{
  print("[INFO] Arquivo de parâmetros não encontrado.")
  print("[INFO] Calculando parâmetros...")
  ch.fit <- est(ch.itens, model = "3PL", engine = "ltm")$est
  print("[INFO] Parâmetros calculados.")
  print("[INFO] Salvando parâmetros...")
  write.csv(ch.fit, file_name)
  print("[INFO] Parâmetros salvos.")
}

print("[INFO] Parâmetros encontrados:")
print(ch.fit)
print("")

print("[INFO] Checando se as notas dos concluintes já foram estimadas...")
file_name = "../Data/Processed/ENEM2009/Estimated Scores/Concluintes_CH.csv"
if(file.exists(file_name)){
  print("[INFO] Arquivo de notas dos concluintes encontrado.")
  ch.score <- data.matrix(read.csv(file_name, row.names = 1))
  ch.scoret <- ch.score <- data.matrix(read.csv("../Data/Processed/ENEM2009/Estimated Scores/Concluintes_CH_0_1000.csv", row.names = 1))
} else{
  print("[INFO] Arquivo de notas dos concluintes não encontrado.")
  print("[INFO] Calculando notas dos concluintes...")
  ch.score <- eap(ch.itens,ch.fit, qu=normal.qu())
  ch.scoret <- ch.score[,1]*(100/sd(ch.score[,1])) + 500 - 100*mean(ch.score[,1])/sd(ch.score[,1])

  print("[INFO] Notas dos concluintes estimadas.")
  print("[INFO] Salvando notas dos concluintes...")
  write.csv(ch.score, file_name)
  write.csv(ch.scoret, "../Data/Processed/ENEM2009/Estimated Scores/Concluintes_CH_0_1000.csv")
  print("[INFO] Notas dos concluintes salvas.")
}

print(paste0("[INFO] Nota média: ", mean(ch.score[,1])))
print(paste0("[INFO] Desvio padrão: ", sd(ch.score[,1])))

hist(ch.scoret, main="Estimated Scores - CH", col=rgb(1,0,0,1/4), xlab="Score", breaks=15,
     ylim=c(0,200000), xlim=c(200,1000))
hist(ch.true_scores, xlab="True Score",  breaks=15, col=rgb(0,0,1,1/4), add=T)

legend("topright",legend=c("True Score", "Estimated Score"), fill = c(rgb(0,0,1,1/4), rgb(1,0,0,1/4)), 
       border = "black")

print(paste0("[INFO] Erro de estimação (RMSE): ", rmse(ch.true_scores, ch.scoret)))