# Figure 10: linear mixed models of annotation scores on inferred commenter gender.
#
# Called by 16_gender_models.py, which writes the model data. Usage:
#   Rscript src/16_gender_models.R <mode> <dir>
#
# reproduce  y ~ gender + (1 | topic) + (1 | author) on the topic-expanded table (one row per
#            comment and blog topic; about 2.9 rows per comment), all 804,437 comments. This
#            is the specification that produced the 7 Oct 2026 Figure 10 (verified to 1e-7).
# revised    y ~ gender + topic indicators + (1 | author), one row per comment, non-empty
#            comments from identifiable users: the model described in the Methods.
# Both: REML, lme4 defaults, male as reference.
suppressPackageStartupMessages({
  library(lme4)
  library(data.table)
})

args <- commandArgs(TRUE)
mode <- args[1]
dir <- args[2]
outcomes <- c("politeness", "emotion_joy", "emotion_fear", "emotion_anger",
              "group_generalization_presence", "toxicity", "hate_speech_presence")

d <- fread(file.path(dir, "model_data.csv"), colClasses = list(character = c("author", "newgender")))
d[, newgender := relevel(factor(newgender), ref = "male")]
topic_cols <- grep("^T_", names(d), value = TRUE)
if (mode == "reproduce") {
  d[, topic := factor(topic)]
  rhs <- "newgender + (1 | topic) + (1 | author)"
} else {
  rhs <- paste("newgender +", paste(topic_cols, collapse = " + "), "+ (1 | author)")
}

est <- list(); vc <- list(); diag <- list(); binned <- list(); re_q <- list(); sd_g <- list()
for (y in outcomes) {
  t0 <- Sys.time()
  m <- lmer(as.formula(paste(y, "~", rhs)), data = d)
  co <- summary(m)$coefficients
  keep <- c("(Intercept)", "newgenderfemale", "newgenderunknown")
  est[[y]] <- data.table(outcome = y, term = keep, estimate = co[keep, 1], se = co[keep, 2], t = co[keep, 3])
  V <- as.matrix(vcov(m))[keep[2:3], keep[2:3]]
  vc[[y]] <- data.table(outcome = y, v_ff = V[1, 1], v_uu = V[2, 2], v_fu = V[1, 2])

  msgs <- m@optinfo$conv$lme4$messages
  vcor <- as.data.frame(VarCorr(m))
  diag[[y]] <- data.table(
    outcome = y, formula = paste(y, "~", rhs), n_obs = nobs(m),
    n_authors = ngrps(m)[["author"]], singular = isSingular(m),
    converged = is.null(msgs), messages = if (is.null(msgs)) "" else paste(msgs, collapse = "; "),
    sd_author = vcor$sdcor[vcor$grp == "author"], sd_residual = sigma(m),
    rank_deficient_dropped = length(attr(getME(m, "X"), "col.dropped")),
    minutes = round(as.numeric(difftime(Sys.time(), t0, units = "mins")), 2)
  )
  if (mode == "revised") {
    f <- fitted(m); r <- resid(m)
    br <- unique(quantile(f, probs = seq(0, 1, length.out = 41)))
    b <- cut(f, br, include.lowest = TRUE)
    binned[[y]] <- data.table(outcome = y, bin = as.integer(b), fitted = f, resid = r)[
      , .(fitted = mean(fitted), resid_mean = mean(resid), resid_sd = sd(resid), n = .N), by = .(outcome, bin)]
    sd_g[[y]] <- data.table(outcome = y, gender = d$newgender, resid = r)[
      , .(resid_sd = sd(resid), n = .N), by = .(outcome, gender)]
    u <- ranef(m)$author[, 1]
    p <- ppoints(length(u))
    idx <- unique(round(seq(1, length(u), length.out = 400)))
    re_q[[y]] <- data.table(outcome = y, theoretical = qnorm(p)[idx], sample = sort(u)[idx] / sd(u))
  }
  cat(sprintf("%s: n=%d, %.1f min, singular=%s, conv=%s\n", y, nobs(m),
              diag[[y]]$minutes, isSingular(m), is.null(msgs)))
  flush(stdout())
}

fwrite(rbindlist(est), file.path(dir, "lmer_estimates.csv"))
fwrite(rbindlist(vc), file.path(dir, "lmer_vcov.csv"))
fwrite(rbindlist(diag), file.path(dir, "lmer_diagnostics.csv"))
if (mode == "revised") {
  fwrite(rbindlist(binned), file.path(dir, "lmer_resid_binned.csv"))
  fwrite(rbindlist(sd_g), file.path(dir, "lmer_resid_sd_by_gender.csv"))
  fwrite(rbindlist(re_q), file.path(dir, "lmer_ranef_qq.csv"))
}
writeLines(capture.output(sessionInfo()), file.path(dir, "sessionInfo_R.txt"))
