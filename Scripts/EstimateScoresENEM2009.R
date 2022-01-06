library(ltm)
library(CTT)
library(Metrics)
require(irtoys)

print("[INFO] Processando dados do ENEM 2009...")

competencias <- c("CN", "CH", "MT", "LC")
for (comp in competencias) {

    print(paste0("[INFO] Começando análise das questões de ", comp))
    print("[INFO] Lendo gabaritos dos alunos concluintes regulares...")

    ch <- read.csv(file=sprintf('../Data/Processed/ENEM2009/Concluintes_regulares_%s.csv',comp))
    ch.itens <- ch[,3:length(ch)]
    ch.true_scores <- ch[,2]

    print("[INFO] Gabaritos lidos.")
    print(paste0("[INFO] Total de participantes: ", nrow(ch)))

    print("[INFO] Checando se os parâmetros já foram calculados...")
    file_name = sprintf("../Data/Processed/ENEM2009/Parameters/Parametros_%s_Concluintes_regulares.csv", comp)
    if(file.exists(file_name)){
      print("[INFO] Arquivo de parâmetros encontrado.")
      ch.fit <- data.matrix(read.csv(file_name, row.names = 1))
      ch.fit_m <- load("../Data/Processed/ENEM2009/Parameters/Fit_%s_Concluintes_regulares.RData")
    } else{
      print("[INFO] Arquivo de parâmetros não encontrado.")
      print("[INFO] Calculando parâmetros...")
      #ch.fit <- est(ch.itens, model = "3PL", engine = "ltm", nqp=40)$est
      ch.fit_m <- tpm(ch.itens, control=list(GHk=40, optimizer="L-BFGS-B"))
      save(ch.fit_m,file="../Data/Processed/ENEM2009/Parameters/Fit_%s_Concluintes_regulares.RData")
      ch.fit <- ch.fit_m$coef
      print("[INFO] Parâmetros calculados.")
      print("[INFO] Salvando parâmetros...")
      write.csv(ch.fit, file_name)
      print("[INFO] Parâmetros salvos.")
    }

    print("[INFO] Parâmetros encontrados:")
    print(ch.fit)
    print("")
    
    ch <- read.csv(file=sprintf('../Data/Processed/ENEM2009/All_%s.csv',comp))
    ch.itens <- ch[,3:length(ch)]
    ch.true_scores <- ch[,2]

    print("[INFO] Checando se as notas já foram estimadas...")
    file_name = sprintf("../Data/Processed/ENEM2009/Estimated Scores/All_%s.csv", comp)
    if(file.exists(file_name)){
      print("[INFO] Arquivo de notas encontrado.")
      ch.score <- data.matrix(read.csv(file_name, row.names = 1))
      ch.scoret <- data.matrix(read.csv(sprintf("../Data/Processed/ENEM2009/Estimated Scores/All_%s_0_1000.csv",
                                                comp), row.names = 1))
    } else{
      print("[INFO] Arquivo de notas não encontrado.")
      print("[INFO] Calculando notas...")
      #ch.score <- eap(ch.itens,ch.fit, qu=normal.qu())[,1]
      ch.score <- factor.scores(ch.fit_m, resp.patterns=ch.itens, method="EAP")$score[,"z1"]
      #ch.scoret <- ch.score[,1]*(100/sd(ch.score[,1])) + 500 - 100*mean(ch.score[,1])/sd(ch.score[,1])
      ch.scoret <- score.transform(ch.score, mu.new=500, sd.new=100, normalize = FALSE)$new.scores

      print("[INFO] Notas estimadas.")
      print("[INFO] Salvando notas...")
      write.csv(ch.score, file_name)
      write.csv(ch.scoret, sprintf("../Data/Processed/ENEM2009/Estimated Scores/All_%s_0_1000.csv", comp))
      print("[INFO] Notas salvas.")
    }

    print(paste0("[INFO] Nota média: ", mean(ch.score)))
    print(paste0("[INFO] Desvio padrão: ", sd(ch.score)))

    png(file=sprintf("../Images/Histogram-%s2009.png",comp))
    hist(ch.scoret, main=sprintf("Histogram of Scores - %s", comp), col=rgb(1,0,0,1/4), xlab="Score", breaks=15,
         ylim=c(0,500000), xlim=c(0,1000))
    hist(ch.true_scores, xlab="True Score",  breaks=15, col=rgb(0,0,1,1/4), add=T)
    legend("topright",legend=c("True Score", "Estimated Score"), fill = c(rgb(0,0,1,1/4), rgb(1,0,0,1/4)), 
           border = "black")
    #---------------------------------------------------------

    png(file=sprintf("../Images/Errors-%s2009.png",comp))
    plot(ch.true_scores, ch.scoret, cex = .1,
        xlab="True Score", ylab="Estimated Score",
        xlim=c(0,1000), ylim=c(0,1000)) 
    abline(a=0, b=1)
    #---------------------------------------------------------
    png(file=sprintf("../Images/Hist_Errors-%s2009.png",comp))
    hist(ch.scoret-ch.true_scores, main=sprintf("Histogram of Errors - %s", comp), col=rgb(1,0,0,1/4), 
        xlab="Error", breaks=15, ylim=c(0,200000), xlim=c(-1000,1000))

    print(paste0("[INFO] Erro de estimação (RMSE): ", rmse(ch.true_scores, ch.scoret)))
    print("-----------------------------------------")
}