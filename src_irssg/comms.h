#ifndef COMMS_H
#define COMMS_H

#ifdef __cplusplus
extern "C" {
#endif

// Common variables from comms module
extern int num_sym, num_k, num_bands, nspin, max_nsym, max_plane, ncnt;
extern double complex* coeffa;
extern double complex* coeffb;
extern double* EE;
extern int* igall;
extern double* KV;
extern double* kpoints_from_outcar;
extern int bot_band, top_band;

// Function declarations
void setarray(void);
void downarray(void);
void read_outcar(void);
void read_wavecar(int kkk);
void read_wavecar_spin_polarized(int kkk);
void get_ssg_from_identifySSG(char* ssg_num, int* num_sym, 
                             int* rot_input, double* tau_input,
                             double complex* SU2_input, double* spin_rot_input,
                             int* time_reversal_input);
void output_ssg_operator(char* ssg_num, int num_sym, int* rot_input,
                        double* tau_input, double complex* SU2_input,
                        double* spin_rot_input, int* time_reversal_input);
void kgroup(int num_sym, int max_sym, int* rot_input, int* time_reversal_input,
            double* WK, int* litt_group, int* num_litt_group);
void get_ch_from_op(int num_litt_group, double* spin_rot, int* rot,
                   double* tau, double complex* SU2, int* time_reversal,
                   double* WK, int* op_order, int* irrep_num,
                   double complex* ch_table, double complex* phase,
                   int* irrep_unitary_num, double complex* ch_unitary_table,
                   int* torsion);
void find_relation_between_unitary_irrep_coirrep(int num_litt_group_unitary,
                                                int irrep_num, double complex* ch_table_less,
                                                int irrep_unitary_num, double complex* ch_unitary_table_less,
                                                int* irrep_coirrep_relation, int* discriminant_value,
                                                int* torsion);
void output_character_table(char* k_name, int num_litt_group, int num_litt_group_unitary,
                           int* litt_group, int* op_order, int irrep_num,
                           double complex* ch_table_less, double complex* phase,
                           int irrep_unitary_num, double complex* ch_unitary_table_less,
                           int* irrep_coirrep_relation, char* irrep_name_list,
                           int* discriminant_value);
void get_comprel(int num_litt_group, int num_litt_group_unitary, int* litt_group,
                int* op_order, int irrep_num, char* irrep_name_list,
                double complex* ch_table_less);
void end_get_comprel(void);
void pw_setup_ssg(double* WK, int num_litt_group_unitary, int max_plane, int ncnt,
                 int* igall, int* rot_unitary, double* SO3_unitary, double* tau_unitary,
                 double complex* kphase, double complex* Gphase, int* tilte_vec);
void get_k_name(double* WK, char* k_name, char* k_frac_symbol);
void judge_up_down_relation(int num_litt_group, double complex* SU2,
                           int* time_reversal, int* spin_no_reversal);

#ifdef __cplusplus
}
#endif

#endif // COMMS_H

