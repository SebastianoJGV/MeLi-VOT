library(tidyverse)
library(lme4)

manData <- read_csv("MeLi/Local code/updated_man.csv")
engData <- read_csv("MeLi/Local code/updated_eng.csv")

wordinitial_man <- filter(manData, as.character(isWordInitial) == TRUE)
wordinitial_eng <- filter(engData, as.character(isWordInitial) == TRUE)
print(wordinitial_eng)
#dataframe_wordinit_list <- ls(pattern = "^wordinit_")

#m <- matrix(data = "", nrow = 1, ncol = 3) 

#for (n in seq_along(dataframe_wordinit_list)) {
#  average_vot <- get(dataframe_wordinit_list[n]) %>%
#       group_by(Source_File) %>% # nolint
#        summarise(mean_VOT = mean(VOT))
#    average_vot$DataFrame_Name <- dataframe_wordinit_list[n]
#    m <- rbind(m, average_vot)
#}
#man_cleaned_word <- wordinitial_man %>%
#  mutate(VOT = ifelse(VOT_Type == "predNEG", VOT * -1, VOT))

sanitisation_func <- function(inputdf){
    inputdf <- inputdf %>%
        mutate(VOT = ifelse(VOT_Type == "predNEG", VOT * -1, VOT))

    inputdf$VOT <- inputdf$VOT*1000
    print('current rows at start:')
    print(nrow(inputdf))

    inputdf <- filter(inputdf, !(-10 <= VOT & VOT <= 10))
    print('current rows after removal of -10 to 10:')
    print(nrow(inputdf))

    inputdf <- inputdf %>% 
    group_by(phone, Source_File) %>% 
    filter(between(VOT, mean(VOT) - 2.5*sd(VOT), mean(VOT) + 2.5*sd(VOT)))


    #print(sanitised_man$VOT)
    print('current rows after removal of 2.5sd to -2.5sd:')
    print(nrow(inputdf))

    return(inputdf)
}

sanitised_eng <- sanitisation_func(wordinitial_eng)
sanitised_man <- sanitisation_func(wordinitial_man)

sanitised_eng %>%
    ggplot(aes(x = VOT)) +
    geom_density() +
    facet_wrap(~ phone, labeller = labeller(phone = ~ paste("Phone:", .))) + 
    theme_bw()

sanitised_man %>%
    ggplot(aes(x = VOT)) +
    geom_density() +
    facet_wrap(~ phone, labeller = labeller(phone = ~ paste("Phone:", .))) + 
    theme_bw()

phones <- unique(sanitised_eng$phone)
#print(sanitised_eng)
    for (p in phones) {
      # Save to a file named 'phone_name.png'
      #ggsave(filename = paste0(p, ".png"))
      
      # Plot the data (it won't show, but it will create the object)
      sanitised_eng %>% 
        filter(phone == p) %>% 
        ggplot(aes(x = VOT)) +
        geom_density() + 
        theme_bw()
    }

phones <- unique(sanitised_man$phone)
#print(sanitised_man)
    for (p in phones) {
      # Save to a file named 'phone_name.png'
      #ggsave(filename = paste0(p, ".png"))
      
      # Plot the data (it won't show, but it will create the object)
      sanitised_eng %>% 
        filter(phone == p) %>% 
        ggplot(aes(x = VOT)) +
        geom_density() + 
        theme_bw()
    }
#print(wilks_eng[[2]])
#print(wilks_man)



# I could just take a ratio?
# Divide VOT my phones per second, chart that output?
# Other option is a linear mixed effect model
eng_models <- sanitised_eng %>%
    group_by(phone) %>%
    nest() %>%
    mutate(model = map(data, ~lmer(VOT ~ phonesPerSecond + (1 | Source_File), data = .x)))
#print(eng_models)

# eng_models$model[[7]]

man_models <- sanitised_man %>%
    group_by(phone) %>%
    nest() %>%
    mutate(model = map(data, ~lmer(VOT ~ phonesPerSecond + (1 | Source_File), data = .x)))
#print(man_models)

#man_models$model[[1]]

#print(sanitised_man$phonesPerSecond)
binList <- c(0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 40)

bins_man <- sanitised_man  %>%
     mutate(PPS_bin = cut(phonesPerSecond, breaks = binList)) 

bins_man %>%
    group_by(phone) %>%
    ggplot(aes(x = PPS_bin, y = VOT)) +
    geom_boxplot() +
    facet_wrap(~ phone, labeller = labeller(phone = ~ paste("Phone:", .))) +  
    theme_bw() 
ggsave("man bins.png", width = 40, height = 40)

bins_eng <- sanitised_eng  %>%
     mutate(PPS_bin = cut(phonesPerSecond, breaks = binList)) 

bins_eng %>%
    group_by(phone) %>%
    ggplot(aes(x = PPS_bin, y = VOT)) +
    geom_boxplot() + 
    facet_wrap(~ phone, labeller = labeller(phone = ~ paste("Phone:", .))) + 
    theme_bw() 
ggsave("eng bins.png", width = 40, height = 40)