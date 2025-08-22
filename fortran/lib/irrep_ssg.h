#ifndef IRREP_SSG_H
#define IRREP_SSG_H

#ifdef __cplusplus
extern "C" {
#endif

// Main function for calculating irreducible representations
void irrep_ssg(int num_litt_group_unitary, int* litt_group_unitary,
               int* rot, double* tau, double* SO3, double complex* SU2,
               int KKK, double* WK, double complex* kphase,
               int num_bands, int m, int n, double* ene_bands,
               int dim_basis, int num_basis,
               double complex* coeffa, double complex* coeffb,
               int irrep_num, double complex* ch_table,
               char* irrep_name_list,
               double complex* G_phase_pw, int* rot_vec_pw);

#ifdef __cplusplus
}
#endif

#endif // IRREP_SSG_H

