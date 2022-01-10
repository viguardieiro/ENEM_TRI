library(ltm)
library(CTT)
library(Metrics)
require(irtoys)

print("[INFO] Processando dados do ENEM 2009...")

regioes <- c("N", "NE", "SE", "S", "CO")
competencias <- c("CN", "CH", "MT", "LC")

for (reg in regioes){
    print(paste0("[INFO] Começando análise da regiao ", reg))
    for (comp in competencias) {

        print(paste0("[INFO] Começando análise das questões de ", comp))
        print("[INFO] Lendo gabaritos dos alunos concluintes regulares...")

        ch <- read.csv(file=sprintf('../Data/Processed/ENEM2009/CR_regiao%s_%s.csv',reg,comp))
        ch.itens <- ch[,3:length(ch)]
        ch.true_scores <- ch[,2]

        print("[INFO] Gabaritos lidos.")
        print(paste0("[INFO] Total de concluintes regulares: ", nrow(ch)))

        print("[INFO] Checando se os parâmetros já foram calculados...")
        file_name = sprintf("../Data/Processed/ENEM2009/Parameters/Parametros_CR_regiao%s_%s.csv", reg, comp)
        if(file.exists(file_name)){
          print("[INFO] Arquivo de parâmetros encontrado.")
          ch.fit <- data.matrix(read.csv(file_name, row.names = 1))
          ch.fit_m <- load(sprintf("../Data/Processed/ENEM2009/Parameters/Fit_CR_regiao%s_%s.Rdata", reg, comp))
        } else{
          print("[INFO] Arquivo de parâmetros não encontrado.")
          print("[INFO] Calculando parâmetros...")
          #ch.fit <- est(ch.itens, model = "3PL", engine = "ltm", nqp=40)$est
          ch.fit_m <- tpm(ch.itens, control=list(GHk=40, optimizer="L-BFGS-B"))
          save(ch.fit_m,file=sprintf("../Data/Processed/ENEM2009/Parameters/Fit_CR_regiao%s_%s.Rdata", reg, comp))
          ch.fit <- ch.fit_m$coef
          print("[INFO] Parâmetros calculados.")
          print("[INFO] Salvando parâmetros...")
          write.csv(ch.fit, file_name)
          print("[INFO] Parâmetros salvos.")
        }

        print("[INFO] Parâmetros encontrados:")
        print(ch.fit)
        print("")
       

        print("[INFO] Checando se as notas já foram estimadas...")
        file_name = sprintf("../Data/Processed/ENEM2009/Estimated Scores/CR_regiao%s_%s.csv", reg, comp)
        if(file.exists(file_name)){
          print("[INFO] Arquivo de notas encontrado.")
          ch.score <- data.matrix(read.csv(file_name, row.names = 1))
          ch.scoret <- data.matrix(read.csv(sprintf("../Data/Processed/ENEM2009/Estimated Scores/CR_regiao%s_%s_0_1000.csv",
                                                    reg, comp), row.names = 1))
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
          write.csv(ch.scoret, sprintf("../Data/Processed/ENEM2009/Estimated Scores/CR_regiao%s_%s_0_1000.csv", reg, comp))
          print("[INFO] Notas salvas.")
        }

        print(paste0("[INFO] Nota média: ", mean(ch.score)))
        print(paste0("[INFO] Desvio padrão: ", sd(ch.score)))

        png(file=sprintf("../Images/Histogram_regiao%s_%s2009.png", reg, comp))
        hist(ch.scoret, main=sprintf("Histogram of Scores - %s - %s", reg, comp), col=rgb(1,0,0,1/4), xlab="Score", breaks=15,
             ylim=c(0,500000), xlim=c(0,1000))
        hist(ch.true_scores, xlab="True Score",  breaks=15, col=rgb(0,0,1,1/4), add=T)
        legend("topright",legend=c("True Score", "Estimated Score"), fill = c(rgb(0,0,1,1/4), rgb(1,0,0,1/4)), 
               border = "black")

        print("-----------------------------------------")
    }
}