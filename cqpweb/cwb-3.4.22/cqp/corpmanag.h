/*
 *  IMS Open Corpus Workbench (CWB)
 *  Copyright (C) 1993-2006 by IMS, University of Stuttgart
 *  Copyright (C) 2007-     by the respective contributers (see file AUTHORS)
 *
 *  This program is free software; you can redistribute it and/or modify it
 *  under the terms of the GNU General Public License as published by the
 *  Free Software Foundation; either version 2, or (at your option) any later
 *  version.
 *
 *  This program is distributed in the hope that it will be useful, but
 *  WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
 *  Public License for more details (in the file "COPYING", or available via
 *  WWW at http://www.gnu.org/copyleft/gpl.html).
 */

#ifndef _cqp_corpmanag_h_
#define _cqp_corpmanag_h_


#include "../cl/cl.h"
#include "../cl/bitfields.h"

#include "cqp.h"
#include "context_descriptor.h"



/**
 * The FieldType object represents the fields (or 'anchor points') of a subcorpus (inc query result).
 *
 * NoField is always the last field (so it can be used to determine range of field type codes)
 * (the mnemonic is NoField = "no field" = "number of field types")
 */
typedef enum _field_type {
  MatchField = 0, MatchEndField, TargetField, KeywordField, NoField
} FieldType;
/*TODO these are really not "fields" meaningfully. A better type would be anchor_match, anchor_matchend, etc. */


/**
 * Underlying enumeration for CorpusType.
 *
 * Gives an identifier for each "type" of corpus CQP can deal with.
 */
enum corpus_type { UNDEF,    /**< undefined status                         */
                   SYSTEM,   /**< system corpus, ie registered corpus      */
                   SUB,      /**< subcorpus which was generated by a query */
                   TEMP,     /**< temporary subcorpus, deleted after query */
                   ALL       /**< any type of corpus                       */
                 };

/**
 * The CorpusType object.
 */
typedef enum corpus_type CorpusType;


/**
 * An enumeration for lowercase vs. uppercase mode.
 */
enum case_mode {LOWER, UPPER};

/**
 * The Range object represents a range of corpus positions - for instance,
 * the range enclosed by an instance of an s-attribute.
 */
typedef struct _Range {
  int      start;     /**< start position of the corpus interval  */
  int      end;       /**< end position of the corpus interval    */
} Range;

/**
 * The CorpusList object records information on a corpus that CQP recognises.
 *
 * This might be an actual corpus in the registry (->type=SYSTEM), or a subcorpus or
 * query result (->type=SUB).
 *
 * Note that CorpusList is a bit of a misnomer, although it IS a linked-list
 * entry object, and CQP keeps information on the "corpora" it currently
 * knows about on such a list, in fact this object is often used for passing
 * around information about individual corpora, queries etc. as well.
 */
typedef struct cl {
  char            *name;         /**< corpus name                                */
  char            *mother_name;  /**< name of the original corpus.               */
  int              mother_size;  /**< size (nr tokens) of mother                 */
  char            *registry;     /**< registry directory of the original corpus. */
  char            *abs_fn;       /**< absolute file name                         */
  CorpusType       type;         /**< type of the corpus                         */

  char            *local_dir;    /**< for unloaded subcorpora, this is the
                                      directory where the subcorpus is stored
                                      on disk; required for delayed loading
                                      (in ensure_corpus_size())                  */

  char            *query_corpus; /**< name of the corpus the query was run on    */
  char            *query_text;   /**< the query text proper                      */

  Boolean          saved;        /**< is the corpus (in its present form) saved
                                      (=stored on disk)?                         */
  Boolean          loaded;       /**< has the corpus been loaded from disk?      */
  Boolean          needs_update; /**< True if saved & loaded & contents changed,
                                      or if not saved */

  Corpus          *corpus;       /**< associated corpus data structure
                                      (from the Corpus Library)                  */

  Range           *range;        /**< an array of corpus intervals               */
  int              size;         /**< number of intervals                        */
  int             *sortidx;      /**< sorting index for intervals                */
  int             *targets;      /**< list of targets                            */
  int             *keywords;     /**< one keyword, for each concordance line     */

  ContextDescriptor *cd;         /**< additional attributes to print -- only
                                      for ``SYSTEM'' corpora                     */

  struct cl       *next;         /**< Next corpus on CQP's linked list.          */
} CorpusList;

/**
 * Global pointer to the "current" corpus.
 */
CorpusList *current_corpus;

///**
// * Global pointer to the head of CQP's linked list of corpora.
// */
//extern CorpusList *corpuslist;
//now not accessed outside corpmanag

/* ---------------------------------------------------------------------- */

/* this should usually be provided by a FIELD or FIELDLABEL token recognised by flex,
   but we _may_ need it for the CQi server */
FieldType field_name_to_type(char *name);
char *field_type_to_name(FieldType field);
//int NrFieldValues(CorpusList *cl, FieldType ft);

/* ---------------------------------------------------------------------- */

void init_global_corpuslist(void);

void free_global_corpuslist(void);

CorpusList *findcorpus(char *s, CorpusType type, int try_recursive_search);

CorpusList *dropcorpus(CorpusList *cl, CorpusList *search_from);

CorpusList *duplicate_corpus(CorpusList *cl, char *new_name, Boolean force_overwrite);

CorpusList *make_temp_corpus(CorpusList *cl, char *new_name);

CorpusList *assign_temp_to_sub(CorpusList *tmp, char *subname);

void drop_temp_corpora(void);

Boolean access_corpus(CorpusList *cl);

Boolean change_corpus(char *name, Boolean silent);

void check_available_corpora(CorpusType ct);

Boolean valid_subcorpus_name(char *corpusname);

Boolean subcorpus_name_is_qualified(const char *corpusname);

char *split_subcorpus_name(const char *corpusname, char *mother_name);

Boolean save_subcorpus(CorpusList *cl, char *fname);

void save_unsaved_subcorpora();

/* Iterate through list of corpora */
CorpusList *FirstCorpusFromList();
CorpusList *NextCorpusFromList(CorpusList *cl);

int set_current_corpus(CorpusList *cp, int force);

int set_current_corpus_name(char *name, int force);

int touch_corpus(CorpusList *cp);

/* IO Functions */

void show_corpora_files(CorpusType type);

void show_corpus_active(void);

#endif
