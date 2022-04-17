setwd("~/Box/PapersAndProjects/walle/mgl/")
read.csv(file="allcontours.txt") -> anal
read.csv(file="classified.txt") -> cla


plot(Y~X, data=anal)
plot(Frame~X, data=anal, cex=0.1)

a <- rle(sort(cla$pulse))
data.frame(number=a$values, n=a$lengths) -> durations
hist(durations$n)
hist(durations$n[which(durations$n > 27)], main="MGL Pulse Duration", col="light blue", xlab="Duration (frames)")


prcomp(anal, center=TRUE, scale.=TRUE) -> all.pca
#plot(all.pca, type = "l")
#biplot(all.pca)

library(devtools)
install_github("ggbiplot", "vqv")
 
library(ggbiplot)
g <- ggbiplot(all.pca, obs.scale = 1, var.scale = 1, 
              ellipse = TRUE, 
              circle = TRUE)
g <- g + scale_color_discrete(name = 'pulse')
g <- g + theme(legend.direction = 'horizontal', 
               legend.position = 'top')
print(g)
